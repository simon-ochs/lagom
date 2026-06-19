import logging
from datetime import timedelta

import numpy as np
import pandas as pd

from app.loader import TZ_OFFSET_HOURS
from app.models import PumpConfig

logger = logging.getLogger("lagom.analysis")

# Algorithm constants (not user-tunable).
EVALUATION_WINDOW_HOURS = 4   # post-bolus CGM window to grade
CGM_MERGE_TOLERANCE = "10 minutes"
HYPO_THRESHOLD = 70           # mg/dL — below this a window is confounded by rescue carbs
GRADE_HIGH = 130              # mg/dL — above is "ratio too weak"
GRADE_LOW = 80                # mg/dL — below is "ratio too strong"
STACKING_SENTINEL = 999.0     # end_glucose for a correction-only follow-up bolus


def _f(x):
    """Convert numpy/NaN scalars to JSON-safe floats (NaN -> None)."""
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    return float(x)


def time_slot(hour):
    if 5 <= hour < 11:
        return "Breakfast"
    if 11 <= hour < 16:
        return "Lunch"
    if 16 <= hour < 22:
        return "Dinner"
    return "Night"


def detect_pod_failures(alarms_df):
    """Pod delivery interruptions — basal is cut off, confounding any window they touch."""
    pod_failures = alarms_df[
        alarms_df["event"].str.contains("delivery stopped", case=False, na=False)
    ].copy()
    logger.info("Detected %d pod failure event(s)", len(pod_failures))
    return pod_failures


def merge_bolus_cgm(bolus_df, cgm_df):
    """Attach each bolus the most recent CGM reading within the merge tolerance."""
    events_df = pd.merge_asof(
        bolus_df,
        cgm_df[["timestamp", "glucose"]],
        on="timestamp",
        direction="backward",
        tolerance=pd.Timedelta(CGM_MERGE_TOLERANCE),
    )
    events_df = events_df[events_df["bolus"] > 0].copy()
    logger.info("Merged %d bolus events with CGM (within %s)", len(events_df), CGM_MERGE_TOLERANCE)
    return events_df


def evaluate_event_window(row, all_events_df, cgm_df, pod_failure_times):
    """Classify the CGM window following a bolus; only 'Clean Window' is gradable."""
    start_time = row["timestamp"]
    end_time = start_time + timedelta(hours=EVALUATION_WINDOW_HOURS)

    failures_in_window = pod_failure_times[
        (pod_failure_times >= start_time) & (pod_failure_times <= end_time)
    ]
    if not failures_in_window.empty:
        return pd.Series({"status": "Rejected: Pod Delivery Interrupted", "end_glucose": np.nan, "min_glucose": np.nan})

    subsequent_boluses = all_events_df[
        (all_events_df["timestamp"] > start_time)
        & (all_events_df["timestamp"] <= end_time)
        & (all_events_df["bolus"] > 0)
    ]
    if not subsequent_boluses.empty:
        # A new meal makes the window unrelated to the first bolus performance.
        if subsequent_boluses["carbs"].fillna(0).sum() > 0:
            return pd.Series({"status": "Rejected: New Meal in Window", "end_glucose": np.nan, "min_glucose": np.nan})
        # A correction-only follow-up signals the first bolus undershot.
        else:
            return pd.Series({"status": "Clean Window", "end_glucose": STACKING_SENTINEL, "min_glucose": np.nan})

    window_cgm = cgm_df[
        (cgm_df["timestamp"] >= start_time) & (cgm_df["timestamp"] <= end_time)
    ]
    if window_cgm.empty:
        return pd.Series({"status": "Rejected: Missing CGM Data", "end_glucose": np.nan, "min_glucose": np.nan})

    end_glucose = window_cgm.iloc[-1]["glucose"]
    min_glucose = window_cgm["glucose"].min()

    status = "Clean Window"
    if min_glucose < HYPO_THRESHOLD:
        status = "Rejected: Hypoglycemic Event Detected"

    return pd.Series({"status": status, "end_glucose": end_glucose, "min_glucose": min_glucose})


def grade_ratio(row):
    if row["end_glucose"] > GRADE_HIGH:
        return "Ratio Too Weak (Failed High)"
    elif row["end_glucose"] < GRADE_LOW:
        return "Ratio Too Strong (Failed Low)"
    else:
        return "Ratio Accurate (In Range)"


def compute_meal_habits(events_df):
    """Infer typical eating patterns from carb boluses, bucketed by time of day."""
    meal_boluses = events_df[events_df["carbs"].fillna(0) > 0].copy()
    if meal_boluses.empty:
        return {}

    meal_boluses["local_hour"] = (
        meal_boluses["timestamp"].dt.hour
        + meal_boluses["timestamp"].dt.minute / 60
        + TZ_OFFSET_HOURS
    ) % 24
    meal_boluses["slot"] = meal_boluses["local_hour"].apply(time_slot)

    habits = meal_boluses.groupby("slot").agg(
        events=("carbs", "count"),
        avg_carbs=("carbs", "mean"),
        avg_bolus=("bolus", "mean"),
        median_hour=("local_hour", "median"),
    )
    return {
        slot: {
            "events": int(row["events"]),
            "avg_carbs": _f(row["avg_carbs"]),
            "avg_bolus": _f(row["avg_bolus"]),
            "median_hour": _f(row["median_hour"]),
        }
        for slot, row in habits.iterrows()
    }


def _implied_isf_from_shortfall(row, config):
    """Back-calculate the ISF a correction bolus implies when it failed high."""
    bg = row["Blood Glucose Input (mg/dl)"]
    if bg <= 0 or row["end_glucose"] >= 900:
        return np.nan
    required_drop = bg - config.target_glucose
    actual_drop = bg - row["end_glucose"]
    shortfall_units = (required_drop - actual_drop) / config.isf
    total_needed = row["bolus"] + shortfall_units
    return required_drop / total_needed if total_needed > 0 else np.nan


def _implied_icr_from_shortfall(row, config):
    """Back-calculate the ICR a meal bolus implies when it failed high."""
    bg = row["Blood Glucose Input (mg/dl)"] if row["Blood Glucose Input (mg/dl)"] > 0 else config.target_glucose
    correction_component = (bg - config.target_glucose) / config.isf
    carb_bolus_given = row["bolus"] - correction_component
    if row["end_glucose"] >= 900 or np.isnan(row["end_glucose"]):
        return np.nan
    shortfall_units = max(0, row["end_glucose"] - config.target_glucose) / config.isf
    total_carb_bolus_needed = carb_bolus_given + shortfall_units
    return row["carbs"] / total_carb_bolus_needed if total_carb_bolus_needed > 0 else np.nan


def _isf_recommendation(implied, configured):
    if implied is None:
        return "insufficient data", None
    if implied < configured - 2:
        return "consider lowering", round(implied / 5) * 5
    if implied > configured + 2:
        return "consider raising", round(implied / 5) * 5
    return "well-calibrated", None


def _icr_recommendation(implied, configured):
    if implied is None:
        return "insufficient data", None
    if implied < configured - 0.4:
        return "consider lowering", round(implied / 0.5) * 0.5
    if implied > configured + 0.4:
        return "consider raising", round(implied / 0.5) * 0.5
    return "well-calibrated", None


def run_analysis(cgm_df, bolus_df, alarms_df, insulin_df, config: PumpConfig) -> dict:
    pod_failures = detect_pod_failures(alarms_df)
    pod_failure_times = pod_failures["timestamp"]

    events_df = merge_bolus_cgm(bolus_df, cgm_df)

    outcomes = events_df.apply(
        evaluate_event_window, axis=1, args=(events_df, cgm_df, pod_failure_times)
    )
    processed_events = pd.concat([events_df, outcomes], axis=1)

    clean_events = processed_events[processed_events["status"] == "Clean Window"].copy()
    clean_events["evaluation"] = clean_events.apply(grade_ratio, axis=1)
    logger.info(
        "Window evaluation: %d clean, %d rejected",
        len(clean_events), len(processed_events) - len(clean_events),
    )

    # ── ISF from correction boluses (no carbs) ──
    corr = clean_events[clean_events["carbs"].fillna(0) == 0].copy()
    corr["implied_isf"] = corr.apply(_implied_isf_from_shortfall, axis=1, args=(config,))
    inferred_isf = _f(corr["implied_isf"].median())
    isf_rec, isf_suggested = _isf_recommendation(inferred_isf, config.isf)
    logger.info(
        "ISF: implied median=%s, configured=%s -> %s",
        inferred_isf, config.isf, isf_rec,
    )

    # ── ICR from meal boluses (with carbs) ──
    meal = clean_events[clean_events["carbs"].fillna(0) > 0].copy()
    meal["implied_icr"] = meal.apply(_implied_icr_from_shortfall, axis=1, args=(config,))
    inferred_icr = _f(meal["implied_icr"].median())
    icr_rec, icr_suggested = _icr_recommendation(inferred_icr, config.icr)
    logger.info(
        "ICR: implied median=%s, configured=%s -> %s",
        inferred_icr, config.icr, icr_rec,
    )

    # ── Time-of-day breakdown of clean-window grades ──
    time_of_day = {}
    if not clean_events.empty:
        clean_events["slot"] = ((clean_events["timestamp"].dt.hour + TZ_OFFSET_HOURS) % 24).apply(time_slot)
        tod = clean_events.groupby("slot")["evaluation"].value_counts().unstack(fill_value=0)
        for slot, row in tod.iterrows():
            time_of_day[slot] = {
                "high": int(row.get("Ratio Too Weak (Failed High)", 0)),
                "ok": int(row.get("Ratio Accurate (In Range)", 0)),
                "low": int(row.get("Ratio Too Strong (Failed Low)", 0)),
            }

    return {
        "summary": {
            "cgm_readings": len(cgm_df),
            "bolus_events": len(events_df),
            "pod_failures": len(pod_failures),
            "clean_windows": len(clean_events),
            "rejected_windows": len(processed_events) - len(clean_events),
        },
        "isf": {
            "configured": config.isf,
            "implied_median": inferred_isf,
            "evaluated": len(corr),
            "trended_high": int((corr["end_glucose"] > config.target_glucose).sum()),
            "recommendation": isf_rec,
            "suggested": _f(isf_suggested),
        },
        "icr": {
            "configured": config.icr,
            "implied_median": inferred_icr,
            "evaluated": len(meal),
            "trended_high": int((meal["end_glucose"] > config.target_glucose).sum()),
            "recommendation": icr_rec,
            "suggested": _f(icr_suggested),
        },
        "meal_habits": compute_meal_habits(events_df),
        "time_of_day_breakdown": time_of_day,
        "daily_summary": _daily_summary(insulin_df, pod_failures),
    }


def _daily_summary(insulin_df, pod_failures):
    df = insulin_df.copy()
    df["date"] = df["timestamp"].dt.date
    df["bolus_pct"] = df["total_bolus"] / df["total_insulin"] * 100
    df["basal_pct"] = df["total_basal"] / df["total_insulin"] * 100

    failure_dates = set(pod_failures["timestamp"].dt.date)
    rows = []
    for _, row in df.sort_values("date").iterrows():
        rows.append({
            "date": str(row["date"]),
            "total_basal": _f(row["total_basal"]),
            "total_bolus": _f(row["total_bolus"]),
            "total_insulin": _f(row["total_insulin"]),
            "basal_pct": _f(row["basal_pct"]),
            "bolus_pct": _f(row["bolus_pct"]),
            "pod_failure": row["date"] in failure_dates,
        })
    return rows

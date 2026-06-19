from pydantic import BaseModel


class PumpConfig(BaseModel):
    """The pump ratios currently programmed — the baseline we evaluate against."""

    icr: float = 10           # insulin-to-carb ratio, g per unit
    isf: float = 30           # insulin sensitivity factor, mg/dL per unit
    target_glucose: float = 110  # mg/dL


class AnalysisResult(BaseModel):
    summary: dict                # event counts: cgm, bolus, pod failures, clean, rejected
    isf: dict                    # configured, implied median, recommendation
    icr: dict                    # configured, implied median, recommendation
    meal_habits: dict            # inferred eating patterns keyed by time-of-day slot
    time_of_day_breakdown: dict  # clean-window grades keyed by slot
    daily_summary: list[dict]    # per-day insulin totals

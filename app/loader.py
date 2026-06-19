import io
import logging
import zipfile

import pandas as pd

logger = logging.getLogger("lagom.loader")

# Glooko exports timestamps in the account's local time, so no UTC shift is needed.
TZ_OFFSET_HOURS = 0

# Paths inside the Glooko export zip.
CGM_PATH = "cgm_data_1.csv"
BOLUS_PATH = "Insulin data/bolus_data_1.csv"
ALARMS_PATH = "alarms_data_1.csv"
INSULIN_PATH = "Insulin data/insulin_data_1.csv"


def load_glooko_zip(zip_bytes: bytes):
    """Read the four CSVs out of a Glooko export zip and return normalized frames.

    Each CSV carries two header rows: a metadata line (name + date range) followed
    by the real column headers, so the metadata line is skipped on read.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        cgm_df = pd.read_csv(zf.open(CGM_PATH), skiprows=1)
        bolus_df = pd.read_csv(zf.open(BOLUS_PATH), skiprows=1)
        alarms_df = pd.read_csv(zf.open(ALARMS_PATH), skiprows=1)
        insulin_df = pd.read_csv(zf.open(INSULIN_PATH), skiprows=1)

    cgm_df = cgm_df.rename(columns={
        "Timestamp": "timestamp",
        "CGM Glucose Value (mg/dl)": "glucose",
    })
    bolus_df = bolus_df.rename(columns={
        "Timestamp": "timestamp",
        "Insulin Delivered (U)": "bolus",
        "Carbs Input (g)": "carbs",
    })
    alarms_df = alarms_df.rename(columns={
        "Timestamp": "timestamp",
        "Alarm/Event": "event",
    })
    insulin_df = insulin_df.rename(columns={
        "Timestamp": "timestamp",
        "Total Bolus (U)": "total_bolus",
        "Total Basal (U)": "total_basal",
        "Total Insulin (U)": "total_insulin",
    })

    for df in (cgm_df, bolus_df, alarms_df, insulin_df):
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    cgm_df = cgm_df.sort_values("timestamp").reset_index(drop=True)
    bolus_df = bolus_df.sort_values("timestamp").reset_index(drop=True)

    logger.info(
        "Loaded ZIP: %d CGM readings, %d bolus events, %d alarms",
        len(cgm_df), len(bolus_df), len(alarms_df),
    )
    return cgm_df, bolus_df, alarms_df, insulin_df

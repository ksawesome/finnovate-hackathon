"""
Relevant Things
---------------
Inputs:
    record (dict): {GL_Account, old_cat, new_cat, ...}
    base_df (pd.DataFrame), feature_cols (list[str]), target_col (str)

Outputs:
    feedback.csv (append-only log)
    dict → {'action': 'deployed'|'rolled_back'|'skipped', ...}

Dependencies:
    pandas, datetime
    internal: src.ml_model

Side Effects:
    Appends to data/feedback.csv, archives after retrain

Usage:
    from src.feedback_handler import collect_feedback, run_retrain_pipeline

Feedback loop and retraining controller for AURA Intelligence Layer.

Responsibilities:
- Persist user corrections into append-only feedback storage (CSV or Mongo).
- Sanitize feedback records.
- Merge feedback with base data for retraining.
- Trigger model retrain and rollback logic from ml_model.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd

from src.ml_model import retrain_with_feedback

logger = logging.getLogger("aura.feedback")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

FEEDBACK_PATH = os.getenv("FEEDBACK_PATH", "data/feedback.csv")


def _ensure_feedback_path() -> str:
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    if not os.path.exists(FEEDBACK_PATH):
        pd.DataFrame(columns=["timestamp", "GL_Account", "old_cat", "new_cat", "Entity", "notes"]).to_csv(
            FEEDBACK_PATH, index=False
        )
    return FEEDBACK_PATH


def _sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and sanitize a single feedback record.
    """
    required = {"GL_Account", "old_cat", "new_cat"}
    missing = required - set(record.keys())
    if missing:
        raise ValueError(f"Missing required feedback fields: {missing}")

    record = {k: (str(v).strip() if v is not None else "") for k, v in record.items()}
    record["timestamp"] = datetime.utcnow().isoformat()
    return record


def collect_feedback(record: dict[str, Any]) -> None:
    """
    Append a new correction record to the feedback CSV (append-only).
    """
    _ensure_feedback_path()
    sanitized = _sanitize_record(record)
    df = pd.DataFrame([sanitized])
    df.to_csv(FEEDBACK_PATH, mode="a", header=False, index=False)
    logger.info("Added feedback: %s → %s for GL %s", record.get("old_cat"), record.get("new_cat"), record.get("GL_Account"))


def get_feedback() -> pd.DataFrame:
    """
    Load feedback data into a DataFrame.
    """
    _ensure_feedback_path()
    return pd.read_csv(FEEDBACK_PATH)


def clear_feedback() -> None:
    """
    Reset feedback log (for testing or full retrain scenarios).
    """
    _ensure_feedback_path()
    pd.DataFrame(columns=["timestamp", "GL_Account", "old_cat", "new_cat", "Entity", "notes"]).to_csv(
        FEEDBACK_PATH, index=False
    )
    logger.info("Feedback log cleared.")


def merge_feedback_with_base(base_df: pd.DataFrame, feedback_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge feedback with base data, overriding category labels where new feedback exists.
    """
    if feedback_df.empty:
        logger.warning("No feedback data to merge.")
        return base_df

    fb_map = feedback_df.set_index("GL_Account")["new_cat"].to_dict()
    base_df = base_df.copy()
    base_df["Category"] = base_df.apply(
        lambda r: fb_map.get(r["GL_Account"], r["Category"]), axis=1
    )
    return base_df


def run_retrain_pipeline(
    base_df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    numeric_features: list | None = None
) -> dict[str, Any]:
    """
    Load feedback, merge with base, retrain using ml_model.retrain_with_feedback(),
    and return retrain summary.
    """
    fb_df = get_feedback()
    if fb_df.empty:
        logger.info("No feedback available; skipping retrain.")
        return {"action": "skipped", "reason": "no_feedback"}

    logger.info("Running retrain pipeline with %d feedback rows", len(fb_df))
    result = retrain_with_feedback(
        base_df=base_df,
        feedback_df=fb_df,
        feature_cols=feature_cols,
        target_col=target_col,
        numeric_features=numeric_features,
    )

    # Optionally clear or archive feedback after successful retrain
    if result.get("action") == "deployed":
        archive_path = FEEDBACK_PATH.replace(".csv", f"_archived_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv")
        os.rename(FEEDBACK_PATH, archive_path)
        logger.info("Feedback archived to %s", archive_path)

    return result


def validate_feedback_integrity() -> dict[str, Any]:
    """
    Simple integrity check for the feedback log: duplicate accounts, invalid mappings, missing data.
    """
    fb_df = get_feedback()
    report = {"duplicates": 0, "invalid": 0, "total": len(fb_df)}

    if fb_df.empty:
        return report

    dup = fb_df["GL_Account"].duplicated().sum()
    report["duplicates"] = int(dup)

    invalid = fb_df[
        (fb_df["old_cat"].isna()) | (fb_df["new_cat"].isna()) | (fb_df["new_cat"] == fb_df["old_cat"])
    ].shape[0]
    report["invalid"] = int(invalid)

    if dup or invalid:
        logger.warning("Feedback integrity issue: %s", report)
    return report

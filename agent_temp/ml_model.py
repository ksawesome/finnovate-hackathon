"""
Relevant Things
---------------
Inputs:
    df (pd.DataFrame) → with feature_cols + target_col
    feature_cols (list[str]), target_col (str)
    numeric_features (list[str], optional)
    feedback_df (pd.DataFrame, optional)

Outputs:
    model_path (str), metrics (dict), run_id (str)
    pipeline (sklearn.Pipeline)

Dependencies:
    pandas, sklearn, mlflow, joblib
    optional: lightgbm, shap

Side Effects:
    Saves model in models/, logs run to mlflow

Usage:
    from src.ml_model import train, predict, retrain_with_feedback

Features:
- RandomForest (default) with optional LightGBM if installed.
- MLflow tracking for runs, metrics, and model artifacts.
- Retrain with feedback and rollback-on-regression logic.
- Prediction helpers, model save/load.
- Explainability via SHAP when available (optional).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Optional imports
try:
    import lightgbm as lgb
    _HAS_LGB = True
except Exception:
    _HAS_LGB = False

try:
    import shap
    _HAS_SHAP = True
except Exception:
    _HAS_SHAP = False

import mlflow
import mlflow.sklearn

# Config / Paths
MODEL_DIR = os.getenv("MODEL_DIR", "models")
DEFAULT_MODEL_FILENAME = "gl_model.pkl"
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT", "aura_gl_models")
ROLLBACK_METRIC = os.getenv("ROLLBACK_METRIC", "f1")  # metric to monitor for rollback
MIN_IMPROVEMENT = float(os.getenv("MIN_IMPROVEMENT", "0.001"))  # minimal relative improvement required

# Logging
logger = logging.getLogger("aura.ml_model")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _ensure_model_dir(path: str = MODEL_DIR):
    os.makedirs(path, exist_ok=True)
    return path


def _build_pipeline(numeric_features: list | None = None):
    """
    Build a pipeline that scales numeric features and then applies a classifier.
    The pipeline returns a sklearn-like object with fit/predict methods.
    """
    # if numeric_features is None, assume all columns are numeric and pipeline will be applied externally
    num_transformer = Pipeline(steps=[("scaler", StandardScaler())])
    preprocessor = ColumnTransformer(
        transformers=[("num", num_transformer, numeric_features)] if numeric_features else [],
        remainder="passthrough"
    )
    return preprocessor


def _choose_model(**kwargs):
    """
    Choose the best available model class: LightGBM if available else RandomForest.
    kwargs are forwarded to the constructor.
    """
    if _HAS_LGB:
        params = dict(
            n_estimators=kwargs.get("n_estimators", 300),
            learning_rate=kwargs.get("learning_rate", 0.1),
            num_leaves=kwargs.get("num_leaves", 31),
            random_state=kwargs.get("random_state", 42),
            n_jobs=-1
        )
        model = lgb.LGBMClassifier(**params)
        logger.info("Using LightGBM classifier")
    else:
        params = dict(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", None),
            min_samples_split=kwargs.get("min_samples_split", 5),
            class_weight=kwargs.get("class_weight", "balanced_subsample"),
            random_state=kwargs.get("random_state", 42),
            n_jobs=-1
        )
        model = RandomForestClassifier(**params)
        logger.info("Using RandomForest classifier")
    return model


def _evaluate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def save_model(pipeline: Pipeline, path: str | None = None) -> str:
    path = path or os.path.join(_ensure_model_dir(), DEFAULT_MODEL_FILENAME)
    joblib.dump(pipeline, path)
    logger.info("Saved model to %s", path)
    return path


def load_model(path: str | None = None) -> Pipeline:
    path = path or os.path.join(_ensure_model_dir(), DEFAULT_MODEL_FILENAME)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at {path}")
    logger.info("Loading model from %s", path)
    return joblib.load(path)


def train(
    df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    numeric_features: list | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
    model_kwargs: dict[str, Any] | None = None,
    experiment_name: str | None = None,
    save_path: str | None = None,
) -> dict[str, Any]:
    """
    Train model with MLflow logging.
    Returns a dict with model, metrics, run_id, model_path.
    """
    model_kwargs = model_kwargs or {}
    experiment_name = experiment_name or MLFLOW_EXPERIMENT_NAME
    mlflow.set_experiment(experiment_name)

    X = df[feature_cols]
    y = df[target_col].astype(str)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    preprocessor = _build_pipeline(numeric_features)
    model = _choose_model(**model_kwargs)

    # Full pipeline: preprocessor -> classifier
    pipeline = Pipeline(steps=[("pre", preprocessor), ("clf", model)])

    with mlflow.start_run(run_name="train_gl_model") as run:
        try:
            logger.info("Starting training run %s", run.info.run_id)
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_val)

            metrics = _evaluate_metrics(y_val.to_numpy(), y_pred)
            logger.info("Validation metrics: %s", metrics)

            # Log params and metrics
            mlflow.log_params({
                "model_type": type(model).__name__,
                "n_features": len(feature_cols),
                **{f"param_{k}": v for k, v in model.get_params().items() if isinstance(v, (int, float, str, bool))}
            })
            for k, v in metrics.items():
                mlflow.log_metric(k, v)

            # Log model artifact
            model_path = save_model(pipeline, save_path)
            mlflow.sklearn.log_model(pipeline, "model")

            # Try to log a small feature importance summary if available
            try:
                if hasattr(pipeline.named_steps["clf"], "feature_importances_"):
                    fi = pipeline.named_steps["clf"].feature_importances_
                    fi_out = {c: float(val) for c, val in zip(feature_cols, fi[: len(feature_cols)], strict=False)}
                    with open(os.path.join(_ensure_model_dir(), "feature_importance.json"), "w") as fh:
                        json.dump(fi_out, fh)
                    mlflow.log_artifact(os.path.join(_ensure_model_dir(), "feature_importance.json"))
            except Exception:
                logger.warning("Could not compute feature importances")

            result = {
                "run_id": run.info.run_id,
                "model_path": model_path,
                "metrics": metrics,
                "pipeline": pipeline
            }
            return result
        except Exception:
            logger.exception("Training failed")
            raise


def predict(df: pd.DataFrame, feature_cols: list, model: Pipeline | None = None) -> pd.DataFrame:
    """
    Predict categories for dataframe and append columns: predicted, prob_{class} (if predict_proba available).
    Returns copy of dataframe with added columns.
    """
    df = df.copy()
    pipeline = model or load_model()
    X = df[feature_cols]
    preds = pipeline.predict(X)
    df["predicted_cat"] = preds
    if hasattr(pipeline, "predict_proba"):
        try:
            probs = pipeline.predict_proba(X)
            # map class probabilities to columns
            for i, cls in enumerate(pipeline.named_steps["clf"].classes_):
                df[f"prob_{cls}"] = probs[:, i]
        except Exception:
            logger.warning("predict_proba failed or not supported")
    return df


def evaluate(df: pd.DataFrame, feature_cols: list, target_col: str, model: Pipeline | None = None) -> dict[str, Any]:
    pipeline = model or load_model()
    X = df[feature_cols]
    y = df[target_col].astype(str)
    preds = pipeline.predict(X)
    metrics = _evaluate_metrics(y.to_numpy(), preds)
    return {"metrics": metrics}


def compute_psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
    """
    Population Stability Index (PSI) to detect distribution shift between arrays.
    Returns PSI value (higher = more shift).
    """
    def _buckets(arr, breaks):
        return np.digitize(arr, breaks, right=False)

    try:
        expected = np.asarray(expected).astype(float)
        actual = np.asarray(actual).astype(float)
    except Exception:
        raise ValueError("PSI requires numeric arrays")

    breaks = np.linspace(min(expected.min(), actual.min()), max(expected.max(), actual.max()), buckets + 1)
    eps = 1e-8
    psi = 0.0
    for i in range(buckets):
        e_perc = np.sum((expected >= breaks[i]) & (expected < breaks[i+1])) / (len(expected) + eps)
        a_perc = np.sum((actual >= breaks[i]) & (actual < breaks[i+1])) / (len(actual) + eps)
        psi += (e_perc - a_perc) * np.log((e_perc + eps) / (a_perc + eps))
    return float(psi)


def retrain_with_feedback(
    base_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    numeric_features: list | None = None,
    monitor_metric: str = ROLLBACK_METRIC,
    min_improvement: float = MIN_IMPROVEMENT,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Retrain model by merging base dataset with feedback, train a new model,
    compare against currently deployed model, and rollback if regression detected.
    Returns dict with retrain metrics and action ('deployed'/'rolled_back').
    """
    if feedback_df is None or feedback_df.empty:
        raise ValueError("No feedback provided")

    merged = pd.concat([base_df, feedback_df], ignore_index=True)
    # Shuffle
    merged = merged.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    # Train new model on merged data (use internal split)
    res = train(merged, feature_cols, target_col, numeric_features, test_size=0.2, random_state=random_state)
    new_metrics = res["metrics"]
    new_model_path = res["model_path"]

    # Evaluate current model on holdout (use small sample from merged)
    current_model = None
    try:
        current_model = load_model()
    except FileNotFoundError:
        logger.info("No existing model found; deploying new model automatically")
        # nothing to compare, deploy new
        return {"action": "deployed", "new_metrics": new_metrics, "model_path": new_model_path}

    # Prepare evaluation set (use 20% holdout from merged)
    holdout = merged.sample(frac=0.2, random_state=random_state)
    X_hold = holdout[feature_cols]
    y_hold = holdout[target_col].astype(str)

    # Predictions
    new_pipeline = res["pipeline"]
    new_preds = new_pipeline.predict(X_hold)
    new_scores = _evaluate_metrics(y_hold.to_numpy(), new_preds)

    curr_preds = current_model.predict(X_hold)
    curr_scores = _evaluate_metrics(y_hold.to_numpy(), curr_preds)

    # Decide based on monitored metric (higher is better)
    new_val = new_scores.get(monitor_metric)
    curr_val = curr_scores.get(monitor_metric)

    logger.info("Current %s: %s, New %s: %s", monitor_metric, curr_val, monitor_metric, new_val)

    if new_val is None or curr_val is None:
        # if metric absent, deploy cautiously
        action = "deployed"
    else:
        # relative improvement
        rel_imp = (new_val - curr_val) / (abs(curr_val) + 1e-12)
        if rel_imp >= min_improvement:
            action = "deployed"
        else:
            action = "rolled_back"

    if action == "deployed":
        # persist new model artifact to default location
        save_model(new_pipeline)
        mlflow.log_metric(f"retrain_{monitor_metric}", new_val)
        return {"action": "deployed", "new_metrics": new_scores, "curr_metrics": curr_scores, "model_path": new_model_path}
    else:
        # delete the new model artifact (not deployed)
        logger.info("Rolling back — new model did not improve %s by %s", monitor_metric, min_improvement)
        try:
            os.remove(new_model_path)
        except Exception:
            logger.warning("Could not remove new model artifact at %s", new_model_path)
        return {"action": "rolled_back", "new_metrics": new_scores, "curr_metrics": curr_scores}


def explain_instance(instance: pd.Series, feature_cols: list, model: Pipeline | None = None) -> dict[str, Any]:
    """
    Explain a single prediction with SHAP if available. Returns a dict with base_value and feature contributions.
    """
    pipeline = model or load_model()
    X = instance[feature_cols].to_frame().T
    if not _HAS_SHAP:
        return {"warning": "shap_not_installed"}

    try:
        clf = pipeline.named_steps["clf"]
        pre = pipeline.named_steps.get("pre")
        # get the array used by model for SHAP
        if pre is not None:
            X_trans = pre.transform(X)
        else:
            X_trans = X.values
        explainer = shap.TreeExplainer(clf)
        shap_vals = explainer.shap_values(X_trans)
        # shap_values returns list per class for multiclass; map them
        out = {"shap_values": None, "base_values": None}
        try:
            out["shap_values"] = [s.tolist() for s in shap_vals]
            out["base_values"] = explainer.expected_value.tolist() if hasattr(explainer, "expected_value") else None
        except Exception:
            out["shap_values"] = shap_vals.tolist()
        return out
    except Exception:
        logger.exception("SHAP explanation failed")
        return {"error": "explain_failed"}


# End of file

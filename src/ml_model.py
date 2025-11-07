"""ML model module."""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier


def train_and_log_model(X, y, model_name: str = "trial_balance_model"):
    """
    Train and log ML model with MLflow.

    Args:
        X: Features.
        y: Target.
        model_name: Name for logging.
    """
    model = RandomForestClassifier()
    model.fit(X, y)
    mlflow.sklearn.log_model(model, model_name)


def load_model(model_name: str):
    """
    Load model from MLflow.

    Args:
        model_name: Name of the model.

    Returns:
        Model object.
    """
    return mlflow.sklearn.load_model(f"models:/{model_name}/latest")

"""
ML Feedback Collection System.

Collects user feedback on ML predictions to improve model accuracy over time.

Features:
- Store feedback in MongoDB
- Track prediction corrections
- Calculate accuracy metrics
- Flag items for retraining
"""

from datetime import datetime

from bson import ObjectId

from src.db.mongodb import get_user_feedback_collection, log_audit_event


class MLFeedbackCollector:
    """Collect and store user feedback on ML predictions."""

    def __init__(self):
        """Initialize feedback collector."""
        self.collection = get_user_feedback_collection()

    def collect_prediction_feedback(
        self,
        account_code: str,
        prediction_type: str,  # 'anomaly', 'priority', 'attention'
        predicted_value: float,
        actual_value: float | None = None,
        feedback_type: str = "correct",  # 'correct', 'incorrect', 'uncertain'
        user_id: str | None = None,
        comments: str | None = None,
        model_version: str = "1.0",
        period: str | None = None,
        entity: str | None = None,
    ) -> str:
        """
        Collect feedback on a single prediction.

        Args:
            account_code: GL account code
            prediction_type: Type of prediction (anomaly/priority/attention)
            predicted_value: Model's predicted value
            actual_value: User-provided actual value (optional)
            feedback_type: User's assessment (correct/incorrect/uncertain)
            user_id: User providing feedback
            comments: Optional comments from user
            model_version: Version of model that made prediction
            period: Period for the account
            entity: Entity for the account

        Returns:
            Feedback ID
        """
        feedback_doc = {
            "feedback_id": str(ObjectId()),
            "account_code": account_code,
            "prediction_type": prediction_type,
            "predicted_value": float(predicted_value),
            "actual_value": float(actual_value) if actual_value is not None else None,
            "feedback_type": feedback_type,
            "user_id": user_id or "anonymous",
            "comments": comments or "",
            "model_version": model_version,
            "period": period,
            "entity": entity,
            "timestamp": datetime.utcnow(),
            "used_for_training": False,  # Flag for continual learning
        }

        result = self.collection.insert_one(feedback_doc)

        # Log audit event
        log_audit_event(
            event_type="ml_feedback_collected",
            entity=entity or "unknown",
            user=user_id or "anonymous",
            description=f"Feedback on {prediction_type} prediction for {account_code}: {feedback_type}",
            metadata={
                "feedback_id": feedback_doc["feedback_id"],
                "prediction_type": prediction_type,
                "feedback_type": feedback_type,
            },
        )

        return feedback_doc["feedback_id"]

    def get_feedback_by_account(
        self, account_code: str, prediction_type: str | None = None
    ) -> list[dict]:
        """
        Get all feedback for a specific account.

        Args:
            account_code: GL account code
            prediction_type: Optional filter by prediction type

        Returns:
            List of feedback documents
        """
        query = {"account_code": account_code}
        if prediction_type:
            query["prediction_type"] = prediction_type

        return list(self.collection.find(query).sort("timestamp", -1))

    def get_feedback_stats(
        self,
        prediction_type: str | None = None,
        model_version: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """
        Calculate feedback statistics.

        Args:
            prediction_type: Filter by prediction type
            model_version: Filter by model version
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Dict with statistics
        """
        query = {}
        if prediction_type:
            query["prediction_type"] = prediction_type
        if model_version:
            query["model_version"] = model_version
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        total_feedback = self.collection.count_documents(query)

        if total_feedback == 0:
            return {
                "total_feedback": 0,
                "correct": 0,
                "incorrect": 0,
                "uncertain": 0,
                "accuracy_rate": 0.0,
                "correction_rate": 0.0,
            }

        # Count by feedback type
        correct = self.collection.count_documents({**query, "feedback_type": "correct"})
        incorrect = self.collection.count_documents({**query, "feedback_type": "incorrect"})
        uncertain = self.collection.count_documents({**query, "feedback_type": "uncertain"})

        # Calculate rates (excluding uncertain)
        deterministic_total = correct + incorrect
        accuracy_rate = (correct / deterministic_total * 100) if deterministic_total > 0 else 0
        correction_rate = (incorrect / total_feedback * 100) if total_feedback > 0 else 0

        return {
            "total_feedback": total_feedback,
            "correct": correct,
            "incorrect": incorrect,
            "uncertain": uncertain,
            "accuracy_rate": accuracy_rate,
            "correction_rate": correction_rate,
        }

    def get_items_for_retraining(
        self,
        prediction_type: str | None = None,
        min_feedback_count: int = 1,
        only_unused: bool = True,
    ) -> list[dict]:
        """
        Get items with feedback that should be used for retraining.

        Args:
            prediction_type: Filter by prediction type
            min_feedback_count: Minimum feedback count per item
            only_unused: Only return feedback not yet used for training

        Returns:
            List of feedback items suitable for retraining
        """
        query = {}
        if prediction_type:
            query["prediction_type"] = prediction_type
        if only_unused:
            query["used_for_training"] = False

        # Get feedback with actual values (corrections)
        query["actual_value"] = {"$ne": None}

        feedback_items = list(self.collection.find(query).sort("timestamp", 1))

        # Group by account and count
        account_feedback = {}
        for item in feedback_items:
            key = f"{item['account_code']}_{item['prediction_type']}"
            if key not in account_feedback:
                account_feedback[key] = []
            account_feedback[key].append(item)

        # Filter by min count
        retraining_items = []
        for key, items in account_feedback.items():
            if len(items) >= min_feedback_count:
                retraining_items.extend(items)

        return retraining_items

    def mark_feedback_used(self, feedback_ids: list[str]):
        """
        Mark feedback as used for training.

        Args:
            feedback_ids: List of feedback IDs to mark
        """
        self.collection.update_many(
            {"feedback_id": {"$in": feedback_ids}},
            {"$set": {"used_for_training": True, "training_timestamp": datetime.utcnow()}},
        )

    def get_recent_feedback(self, limit: int = 50) -> list[dict]:
        """
        Get most recent feedback items.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of recent feedback documents
        """
        return list(self.collection.find().sort("timestamp", -1).limit(limit))

    def delete_feedback(self, feedback_id: str) -> bool:
        """
        Delete a feedback item.

        Args:
            feedback_id: Feedback ID to delete

        Returns:
            True if deleted, False otherwise
        """
        result = self.collection.delete_one({"feedback_id": feedback_id})
        return result.deleted_count > 0


# Convenience functions for Streamlit
def collect_feedback(
    account_code: str,
    prediction_type: str,
    predicted_value: float,
    actual_value: float | None = None,
    feedback_type: str = "correct",
    user_id: str | None = None,
    comments: str | None = None,
) -> str:
    """
    Quick feedback collection function.

    Args:
        account_code: GL account code
        prediction_type: Type of prediction
        predicted_value: Predicted value
        actual_value: Actual value (if provided)
        feedback_type: Feedback type
        user_id: User ID
        comments: Comments

    Returns:
        Feedback ID
    """
    collector = MLFeedbackCollector()
    return collector.collect_prediction_feedback(
        account_code=account_code,
        prediction_type=prediction_type,
        predicted_value=predicted_value,
        actual_value=actual_value,
        feedback_type=feedback_type,
        user_id=user_id,
        comments=comments,
    )


def get_feedback_statistics(prediction_type: str | None = None) -> dict:
    """
    Get feedback statistics.

    Args:
        prediction_type: Optional filter

    Returns:
        Statistics dict
    """
    collector = MLFeedbackCollector()
    return collector.get_feedback_stats(prediction_type=prediction_type)

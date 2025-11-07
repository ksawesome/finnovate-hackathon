"""
Structured logging configuration for Project Aura
Provides consistent JSON-formatted logging across all modules
"""

import json
import logging
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """
    Structured logger with JSON formatting

    Event Taxonomy:
    - file_uploaded: CSV file received
    - data_profiled: Data profiling completed
    - schema_validated: Schema mapping validated
    - fingerprint_created: SHA-256 hash generated
    - ingestion_started: Ingestion process started
    - ingestion_completed: Ingestion process completed
    - db_insert: Database insertion event
    - error_occurred: Error event
    """

    def __init__(self, name: str, log_file: str = "logs/aura.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if self.logger.handlers:
            return

        # Create logs directory
        Path("logs").mkdir(exist_ok=True)

        # File handler with JSON formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self._json_formatter())

        # Console handler with readable formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _json_formatter(self):
        """Create JSON formatter"""

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }

                # Add extra fields if present
                if hasattr(record, "event_type"):
                    log_data["event_type"] = record.event_type
                if hasattr(record, "metadata"):
                    log_data["metadata"] = record.metadata

                return json.dumps(log_data)

        return JsonFormatter()

    def log_event(
        self, event_type: str, message: str | None = None, level: str = "INFO", **metadata
    ):
        """
        Log structured event

        Args:
            event_type: Event taxonomy type
            message: Optional message
            level: Log level (INFO, WARNING, ERROR)
            **metadata: Additional key-value pairs
        """
        log_message = message or event_type

        extra = {"event_type": event_type, "metadata": metadata}

        if level == "INFO":
            self.logger.info(log_message, extra=extra)
        elif level == "WARNING":
            self.logger.warning(log_message, extra=extra)
        elif level == "ERROR":
            self.logger.error(log_message, extra=extra)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log_event("info", message, "INFO", **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log_event("warning", message, "WARNING", **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log_event("error", message, "ERROR", **kwargs)


# Global logger instance
logger = StructuredLogger("aura")

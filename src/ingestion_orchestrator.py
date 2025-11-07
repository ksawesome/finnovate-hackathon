"""Batch ingestion orchestrator for handling multi-entity ingestion flows."""

from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from .data_ingestion import IngestionOrchestrator
from .utils.logging_config import StructuredLogger

logger = StructuredLogger("batch_ingestion")


class BatchIngestionOrchestrator:
    """Coordinate ingestion for multiple entities with retry and cancellation support."""

    def __init__(self, max_workers: int = 3, max_retries: int = 3) -> None:
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.orchestrator = IngestionOrchestrator()
        self.cancelled = False

    def ingest_batch(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Ingest a batch of files concurrently.

        Each entry in *files* must provide ``file_path``, ``entity``, and ``period`` keys.
        """
        self.cancelled = False

        file_count = len(files)
        logger.log_event("batch_ingestion_started", file_count=file_count)

        if file_count == 0:
            logger.warning("No files supplied for batch ingestion")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0,
                "results": [],
            }

        results: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map: Dict[Future, Dict[str, str]] = {
                executor.submit(
                    self._ingest_with_retry,
                    file_info["file_path"],
                    file_info["entity"],
                    file_info["period"],
                ): file_info
                for file_info in files
            }

            for future in as_completed(future_map):
                if self.cancelled:
                    logger.warning("Batch ingestion cancelled")
                    self._cancel_pending_futures(future_map)
                    break

                file_info = future_map[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(
                        "Batch item completed",
                        entity=file_info["entity"],
                        period=file_info["period"],
                        status=result.get("status"),
                    )
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.error(
                        "Batch item failed with unexpected error",
                        entity=file_info["entity"],
                        period=file_info["period"],
                        error=str(exc),
                    )
                    results.append(
                        {
                            "status": "failed",
                            "entity": file_info["entity"],
                            "period": file_info["period"],
                            "error": str(exc),
                        }
                    )

        successful = len([r for r in results if r.get("status") == "success"])
        failed = len([r for r in results if r.get("status") == "failed"])
        skipped = len([r for r in results if r.get("status") == "skipped"])

        logger.log_event(
            "batch_ingestion_completed",
            total=file_count,
            successful=successful,
            failed=failed,
            skipped=skipped,
            cancelled=self.cancelled,
        )

        return {
            "total": file_count,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "results": results,
        }

    def _ingest_with_retry(self, file_path: str, entity: str, period: str) -> Dict[str, Any]:
        """Run ingestion with exponential backoff retry (1s, 2s, 4s)."""
        for attempt in range(self.max_retries):
            try:
                result = self.orchestrator.ingest_file(
                    file_path=file_path,
                    entity=entity,
                    period=period,
                )

                status = result.get("status")
                if status in {"success", "skipped"}:
                    return result

                if attempt < self.max_retries - 1:
                    delay = 2**attempt
                    logger.warning(
                        "Retrying ingestion after failure",
                        entity=entity,
                        period=period,
                        attempt=attempt + 1,
                        delay_seconds=delay,
                    )
                    time.sleep(delay)
            except Exception as exc:  # pragma: no cover - defensive logging
                if attempt < self.max_retries - 1:
                    delay = 2**attempt
                    logger.warning(
                        "Retrying ingestion after exception",
                        entity=entity,
                        period=period,
                        attempt=attempt + 1,
                        delay_seconds=delay,
                        error=str(exc),
                    )
                    time.sleep(delay)
                else:
                    raise

        return {
            "status": "failed",
            "entity": entity,
            "period": period,
            "error": "Max retries exceeded",
        }

    def cancel(self) -> None:
        """Cancel the current batch run."""
        self.cancelled = True
        logger.warning("Batch ingestion cancellation requested")

    @staticmethod
    def _cancel_pending_futures(future_map: Dict[Future, Dict[str, str]]) -> None:
        """Cancel any futures that have not yet completed."""
        for future in future_map:
            if not future.done():
                future.cancel()

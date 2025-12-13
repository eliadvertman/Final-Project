"""Job monitor manager that orchestrates training and prediction monitors."""

import asyncio
from typing import Optional, Dict, Any

from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.poller.prediction_job_monitor import PredictionJobMonitor
from stroke_seg.bl.poller.training_job_monitor import TrainingJobMonitor
from stroke_seg.bl.poller.evaluation_job_monitor import EvaluationJobMonitor
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.logging_config import get_logger


class JobMonitorManager:
    """Manager that orchestrates training, prediction, and evaluation job monitors."""

    def __init__(
        self,
        job_dao: Optional[JobDAO] = None,
        slurm_client: Optional[SlurmClient] = None,
        poll_interval: int = None
    ):
        """
        Initialize job monitor manager.

        Args:
            job_dao: JobDAO instance (creates new one if None)
            slurm_client: SlurmClient instance (creates new one if None)
            poll_interval: Polling interval in seconds (default from env or 30)
        """
        self.logger = get_logger(__name__)

        # Initialize all monitors with shared dependencies
        self.training_monitor = TrainingJobMonitor(job_dao, slurm_client, poll_interval)
        self.prediction_monitor = PredictionJobMonitor(job_dao, slurm_client, poll_interval)
        self.evaluation_monitor = EvaluationJobMonitor(job_dao, slurm_client, poll_interval)

        self._running = False

    async def start(self) -> None:
        """Start all monitoring services."""
        if self._running:
            self.logger.warning("JobMonitorManager is already running")
            return

        self.logger.info("Starting JobMonitorManager...")

        try:
            # Start all monitors concurrently
            await asyncio.gather(
                self.training_monitor.start(),
                self.prediction_monitor.start(),
                self.evaluation_monitor.start()
            )

            self._running = True
            self.logger.info("JobMonitorManager started successfully - all monitors running")

        except Exception as e:
            self.logger.error(f"Failed to start JobMonitorManager: {str(e)}", exc_info=True)
            # If either monitor fails to start, stop the other one
            await self._stop_monitors()
            raise

    async def stop(self) -> None:
        """Stop both monitoring services gracefully."""
        if not self._running:
            self.logger.warning("JobMonitorManager is not running")
            return

        self.logger.info("Stopping JobMonitorManager...")
        await self._stop_monitors()
        self._running = False
        self.logger.info("JobMonitorManager stopped successfully")

    async def _stop_monitors(self) -> None:
        """Stop all monitors, handling any exceptions."""
        stop_tasks = []

        if self.training_monitor.is_running:
            stop_tasks.append(self.training_monitor.stop())

        if self.prediction_monitor.is_running:
            stop_tasks.append(self.prediction_monitor.stop())

        if self.evaluation_monitor.is_running:
            stop_tasks.append(self.evaluation_monitor.stop())

        if stop_tasks:
            try:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Error stopping monitors: {str(e)}")

    @property
    def is_running(self) -> bool:
        """Check if manager is currently running."""
        return self._running and (
            self.training_monitor.is_running or 
            self.prediction_monitor.is_running or 
            self.evaluation_monitor.is_running
        )

    async def poll_job_once(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Poll a specific job once and return its status.
        Delegates to the appropriate monitor based on job type.

        Args:
            job_id: Internal job UUID as string

        Returns:
            Job status information or None if job not found
        """
        # Try training monitor first
        result = await self.training_monitor.poll_job_once(job_id)
        if result:
            return result

        # Try prediction monitor if not found in training
        result = await self.prediction_monitor.poll_job_once(job_id)
        if result:
            return result

        # Try evaluation monitor if not found in prediction
        result = await self.evaluation_monitor.poll_job_once(job_id)
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information for all monitors."""
        return {
            'manager_running': self.is_running,
            'training_monitor': self.training_monitor.get_status(),
            'prediction_monitor': self.prediction_monitor.get_status(),
            'evaluation_monitor': self.evaluation_monitor.get_status()
        }

    def get_training_monitor(self) -> TrainingJobMonitor:
        """Get the training monitor instance for direct access if needed."""
        return self.training_monitor

    def get_prediction_monitor(self) -> PredictionJobMonitor:
        """Get the prediction monitor instance for direct access if needed."""
        return self.prediction_monitor

    def get_evaluation_monitor(self) -> EvaluationJobMonitor:
        """Get the evaluation monitor instance for direct access if needed."""
        return self.evaluation_monitor
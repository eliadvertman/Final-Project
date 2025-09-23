"""Base abstract class for job monitoring services."""

import asyncio
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.client.slurm.slurm_parser import (
    is_valid_state_transition,
    should_monitor_job_status,
    get_state_transition_reason
)
from stroke_seg.dao.database import database
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.models import JobRecord
from stroke_seg.logging_config import get_logger


class BaseJobMonitor(ABC):
    """Abstract base class for job monitoring services."""

    def __init__(
        self,
        job_dao: Optional[JobDAO] = None,
        slurm_client: Optional[SlurmClient] = None,
        poll_interval: int = None,
        job_type: str = None
    ):
        """
        Initialize base job monitor.

        Args:
            job_dao: JobDAO instance (creates new one if None)
            slurm_client: SlurmClient instance (creates new one if None)
            poll_interval: Polling interval in seconds (default from env or 30)
            job_type: Type of jobs this monitor handles (e.g., 'TRAINING', 'INFERENCE')
        """
        self.logger = get_logger(__name__)
        self.job_dao = job_dao or JobDAO()
        self.slurm_client = slurm_client or SlurmClient()
        self.poll_interval = poll_interval or int(os.getenv('SLURM_POLL_INTERVAL', '30'))
        self.job_type = job_type

        self._running = False
        self._task: Optional[asyncio.Task] = None

        self.logger.info(f"{self.__class__.__name__} initialized with {self.poll_interval}s polling interval")

    async def start(self) -> None:
        """Start the polling service."""
        if self._running:
            self.logger.warning(f"{self.__class__.__name__} is already running")
            return

        try:
            # Initialize database connection for this thread
            self._ensure_database_connection()
            self.logger.info("Database connection established for poller thread")
        except Exception as e:
            self.logger.error(f"Failed to establish database connection for poller: {str(e)}", exc_info=True)
            raise

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        self.logger.info(f"{self.__class__.__name__} started successfully")

    async def stop(self) -> None:
        """Stop the polling service gracefully."""
        if not self._running:
            self.logger.warning(f"{self.__class__.__name__} is not running")
            return

        self._running = False

        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning(f"{self.__class__.__name__} stop timeout, cancelling task")
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

        self.logger.info(f"{self.__class__.__name__} stopped")

        # Clean up database connection
        try:
            if not database.is_closed():
                database.close()
                self.logger.debug("Database connection closed for poller thread")
        except Exception as e:
            self.logger.warning(f"Error closing database connection in poller: {str(e)}")

    @property
    def is_running(self) -> bool:
        """Check if poller is currently running."""
        return self._running and self._task and not self._task.done()

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        self.logger.info(f"{self.__class__.__name__} polling loop started")

        while self._running:
            try:
                await self._poll_active_jobs()
                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                self.logger.info(f"{self.__class__.__name__} polling loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in polling loop: {str(e)}", exc_info=True)

                # Check if it's a database-related error and try to recover
                if "database" in str(e).lower() or "connection" in str(e).lower():
                    self.logger.warning("Database error detected, attempting to reconnect...")
                    try:
                        self._ensure_database_connection()
                        self.logger.info("Database reconnection successful")
                    except Exception as reconnect_error:
                        self.logger.error(f"Failed to reconnect database: {str(reconnect_error)}")

                # Continue polling even if there's an error
                await asyncio.sleep(self.poll_interval)

        self.logger.info(f"{self.__class__.__name__} polling loop ended")

    def _ensure_database_connection(self) -> None:
        """
        Ensure database connection is available in the current thread.

        This is critical for the poller thread which runs separately from Flask.
        """
        try:
            if database.is_closed():
                self.logger.debug("Database connection closed, reconnecting...")
                database.connect()
                self.logger.debug("Database connection established in poller thread")
            else:
                # Test the connection to make sure it's still valid
                database.execute_sql("SELECT 1")

        except Exception as e:
            self.logger.warning(f"Database connection issue in poller thread: {str(e)}")
            try:
                # Force close and reconnect
                if not database.is_closed():
                    database.close()
                database.connect()
                self.logger.info("Database reconnected successfully in poller thread")
            except Exception as reconnect_error:
                self.logger.error(f"Failed to reconnect database in poller thread: {str(reconnect_error)}")
                raise

    @abstractmethod
    def _get_jobs_to_monitor(self) -> List[JobRecord]:
        """
        Get list of jobs this monitor should handle.

        Returns:
            List of JobRecord instances to monitor
        """
        pass

    async def _poll_active_jobs(self) -> None:
        """Poll all active jobs and update their status."""
        try:
            # Ensure database connection is available in this thread
            self._ensure_database_connection()

            # Get jobs this monitor should handle
            jobs_to_monitor = self._get_jobs_to_monitor()

            # Filter jobs to only monitor those in monitorable states (state machine requirement)
            monitorable_jobs = [job for job in jobs_to_monitor if should_monitor_job_status(job.status)]

            if not monitorable_jobs:
                self.logger.debug("No monitorable jobs to poll")
                if jobs_to_monitor:
                    self.logger.debug(f"Skipped {len(jobs_to_monitor) - len(monitorable_jobs)} jobs in terminal states")
                return

            self.logger.info(f"Polling {len(monitorable_jobs)} monitorable jobs (filtered from {len(jobs_to_monitor)} active jobs)")

            # Process each monitorable job
            for job in monitorable_jobs:
                try:
                    await self._update_job_status(job)
                except Exception as e:
                    self.logger.error(f"Failed to update job {job.id} (sbatch_id: {job.sbatch_id}): {str(e)}", exc_info=True)
                    # Continue with other jobs even if one fails
                    continue

        except Exception as e:
            self.logger.error(f"Failed to poll active jobs: {str(e)}", exc_info=True)
            # Don't re-raise - allow polling to continue

    async def _update_job_status(self, job: JobRecord) -> None:
        """
        Update status of a single job with state machine validation.

        Args:
            job: JobRecord to update
        """
        try:
            # Get current job information from SLURM
            job_info = self.slurm_client.get_job_info(job.sbatch_id)

            if not job_info:
                self.logger.warning(f"No job info returned for job {job.id} (sbatch_id: {job.sbatch_id})")
                return

            current_status = job.status
            new_status = job_info.get('internal_status')
            slurm_state = job_info.get('state')
            start_time = job_info.get('start_time')
            end_time = job_info.get('end_time')
            is_finished = job_info.get('is_finished', False)
            error_message = job_info.get('error_message')

            # Special handling for jobs that are no longer in SLURM queue
            if slurm_state == 'NOT_FOUND':
                self.logger.info(f"Job {job.id} (sbatch_id: {job.sbatch_id}) no longer in SLURM queue - "
                               f"marking as completed (was {current_status})")

            self.logger.debug(f"Job {job.id} (sbatch_id: {job.sbatch_id}) - SLURM state: {slurm_state}, "
                             f"Current status: {current_status}, New status: {new_status}")

            # Validate state transition
            if not is_valid_state_transition(current_status, new_status):
                self.logger.error(f"Invalid state transition for job {job.id}: {current_status} -> {new_status}. "
                                f"SLURM state: {slurm_state}. Skipping update.")
                return

            # Check if status has changed or timestamps need updating
            status_changed = current_status != new_status
            timestamps_need_update = self._should_update_timestamps(job, start_time, end_time)

            if status_changed or timestamps_need_update:
                # Delegate to subclass for job-specific handling
                success = await self._handle_job_update(job, job_info, current_status, new_status)

                if success:
                    if status_changed:
                        transition_reason = get_state_transition_reason(current_status, new_status, job_info)
                        self.logger.info(f"Job {job.id} (sbatch_id: {job.sbatch_id}) - {transition_reason}")

                    if is_finished:
                        self.logger.info(f"Job {job.id} reached terminal state: {new_status}")
                else:
                    self.logger.error(f"Failed to handle job update for {job.id}")
            else:
                self.logger.debug(f"No updates needed for job {job.id} - status unchanged: {current_status}")

        except Exception as e:
            # Log error but don't re-raise to avoid stopping the polling of other jobs
            self.logger.error(f"Error updating job {job.id} (sbatch_id: {job.sbatch_id}): {str(e)}", exc_info=True)

    def _should_update_timestamps(self, job: JobRecord, start_time: Optional[datetime], end_time: Optional[datetime]) -> bool:
        """
        Check if timestamps should be updated.

        Args:
            job: Current job record
            start_time: New start time from SLURM
            end_time: New end time from SLURM

        Returns:
            True if timestamps should be updated
        """
        return (start_time and not job.start_time) or (end_time and not job.end_time)

    @abstractmethod
    async def _handle_job_update(self, job: JobRecord, job_info: dict, current_status: str, new_status: str) -> bool:
        """
        Handle job status update. Subclasses implement job-type specific logic.

        Args:
            job: The job record to update
            job_info: Job information from SLURM
            current_status: Current job status
            new_status: New job status from SLURM

        Returns:
            True if update was successful, False otherwise
        """
        pass

    async def poll_job_once(self, job_id: str) -> Optional[dict]:
        """
        Poll a specific job once and return its status.

        Args:
            job_id: Internal job UUID as string

        Returns:
            Job status information or None if job not found
        """
        try:
            # Convert string job_id to UUID for DAO query
            job_uuid = uuid.UUID(job_id)
            job = self.job_dao.get_by_id(job_uuid)
            if not job:
                self.logger.warning(f"Job {job_id} not found")
                return None

            job_info = self.slurm_client.get_job_info(job.sbatch_id)
            return job_info

        except ValueError as e:
            self.logger.error(f"Invalid UUID format for job_id {job_id}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to poll job {job_id}: {str(e)}")
            return None

    def get_status(self) -> dict:
        """Get poller status information."""
        return {
            'monitor_type': self.__class__.__name__,
            'job_type': self.job_type,
            'is_running': self.is_running,
            'poll_interval': self.poll_interval,
            'task_status': 'running' if self._task and not self._task.done() else 'stopped'
        }
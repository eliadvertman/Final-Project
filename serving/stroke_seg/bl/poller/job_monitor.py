"""Async job poller service for monitoring SLURM jobs."""

import asyncio
import os
import uuid
from typing import Optional
from datetime import datetime

from stroke_seg.logging_config import get_logger
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.models import JobRecord, TrainingRecord, ModelRecord
from stroke_seg.dao.database import database
from stroke_seg.dao.training_dao import TrainingDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.client.slurm.slurm_parser import (
    is_valid_state_transition, 
    should_monitor_job_status,
    get_state_transition_reason
)


class JobsMonitor:
    """Async service for polling SLURM job status and updating database."""
    
    def __init__(
        self,
        job_dao: Optional[JobDAO] = None,
        slurm_client: Optional[SlurmClient] = None,
        poll_interval: int = None
    ):
        """
        Initialize job poller.

        Args:
            job_dao: JobDAO instance (creates new one if None)
            slurm_client: SlurmClient instance (creates new one if None)
            poll_interval: Polling interval in seconds (default from env or 30)
        """
        self.logger = get_logger(__name__)
        self.job_dao = job_dao or JobDAO()
        self.training_dao = TrainingDAO()
        self.model_dao = ModelDAO()
        self.slurm_client = slurm_client or SlurmClient()
        self.poll_interval = poll_interval or int(os.getenv('SLURM_POLL_INTERVAL', '30'))
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        self.logger.info(f"JobPoller initialized with {self.poll_interval}s polling interval")
    
    async def start(self) -> None:
        """Start the polling service."""
        if self._running:
            self.logger.warning("JobPoller is already running")
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
        self.logger.info("JobPoller started successfully")
    
    async def stop(self) -> None:
        """Stop the polling service gracefully."""
        if not self._running:
            self.logger.warning("JobPoller is not running")
            return
        
        self._running = False
        
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning("JobPoller stop timeout, cancelling task")
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("JobPoller stopped")
        
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
        self.logger.info("JobPoller polling loop started")
        
        while self._running:
            try:
                await self._poll_active_jobs()
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                self.logger.info("JobPoller polling loop cancelled")
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
        
        self.logger.info("JobPoller polling loop ended")
    
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
    
    async def _poll_active_jobs(self) -> None:
        """Poll all active jobs and update their status."""
        try:
            # Ensure database connection is available in this thread
            self._ensure_database_connection()
            
            # Get all jobs with PENDING or RUNNING status (non-terminal states)
            active_jobs = self.job_dao.get_active_jobs()
            
            # Filter jobs to only monitor those in monitorable states (state machine requirement)
            monitorable_jobs = [job for job in active_jobs if should_monitor_job_status(job.status)]
            
            if not monitorable_jobs:
                self.logger.debug("No monitorable jobs to poll")
                if active_jobs:
                    self.logger.debug(f"Skipped {len(active_jobs) - len(monitorable_jobs)} jobs in terminal states")
                return
            
            self.logger.info(f"Polling {len(monitorable_jobs)} monitorable jobs (filtered from {len(active_jobs)} active jobs)")
            
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
                # Special handling for training job completion
                if job.job_type == 'TRAINING' and new_status == 'COMPLETED':
                    self.logger.info(f"Training job {job.id} completed, handling with transaction")
                    success = self._handle_training_completion(job, job_info)
                    if success:
                        transition_reason = get_state_transition_reason(current_status, new_status, job_info)
                        self.logger.info(f"Job {job.id} (sbatch_id: {job.sbatch_id}) - {transition_reason}")
                        if is_finished:
                            self.logger.info(f"Job {job.id} reached terminal state: {new_status}")
                    else:
                        self.logger.error(f"Failed to handle training completion for job {job.id}")
                else:
                    # Normal job update logic for non-training jobs or non-completion states
                    # Prepare update data
                    update_data = {'status': new_status}

                    # Update timestamps if available and not already set
                    if start_time and not job.start_time:
                        update_data['start_time'] = start_time

                    if end_time and not job.end_time:
                        update_data['end_time'] = end_time

                    # For NOT_FOUND jobs, ensure we have an end time even if start time is unknown
                    if slurm_state == 'NOT_FOUND' and not job.end_time and end_time:
                        update_data['end_time'] = end_time
                        self.logger.debug(f"Setting completion time for missing job {job.id}: {end_time}")

                    # Add error message for failed jobs
                    if new_status == 'FAILED' and error_message:
                        update_data['error_message'] = error_message
                        self.logger.warning(f"Job {job.id} failed: {error_message}")

                    # Update job record in database
                    job_uuid = uuid.UUID(job.id)
                    updated_job = self.job_dao.update(job_uuid, **update_data)

                    if updated_job:
                        if status_changed:
                            transition_reason = get_state_transition_reason(current_status, new_status, job_info)
                            self.logger.info(f"Job {job.id} (sbatch_id: {job.sbatch_id}) - {transition_reason}")

                        if timestamps_need_update:
                            self.logger.debug(f"Updated timestamps for job {job.id}")

                        if is_finished:
                            self.logger.info(f"Job {job.id} reached terminal state: {new_status}")

                    else:
                        self.logger.error(f"Failed to update job {job.id} in database")
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

    def _handle_training_completion(self, job: JobRecord, job_info: dict) -> bool:
        """
        Handle training job completion in a single transaction.
        Updates job status to COMPLETED, training status to TRAINED, and creates model record.

        Args:
            job: The job record to update
            job_info: Job information from SLURM

        Returns:
            True if transaction completed successfully, False otherwise
        """
        try:
            job_uuid = uuid.UUID(job.id)
            start_time = job_info.get('start_time')
            end_time = job_info.get('end_time')

            with database.atomic():
                # Update job record to COMPLETED
                job_update_data = {'status': 'COMPLETED'}
                if start_time and not job.start_time:
                    job_update_data['start_time'] = start_time
                if end_time and not job.end_time:
                    job_update_data['end_time'] = end_time

                updated_job = self.job_dao.update(job_uuid, **job_update_data)
                if not updated_job:
                    self.logger.error(f"Failed to update job {job.id} to COMPLETED")
                    return False

                # Find and update corresponding training record
                training = self.training_dao.get_by_job_id(job_uuid)
                if not training:
                    self.logger.error(f"No training record found for completed job {job.id}")
                    return False

                training_uuid = uuid.UUID(training.id)
                training_update_data = {'status': 'TRAINED'}
                if end_time:
                    training_update_data['end_time'] = end_time

                updated_training = self.training_dao.update(training_uuid, **training_update_data)
                if not updated_training:
                    self.logger.error(f"Failed to update training {training.id} to TRAINED")
                    return False

                # Create model record
                model_record = ModelRecord(
                    training_id=training.id,
                    model_name=f"{training.name}_model",
                    created_at=end_time or datetime.now()
                )
                created_model = self.model_dao.create(model_record)
                if not created_model:
                    self.logger.error(f"Failed to create model record for training {training.id}")
                    return False

                self.logger.info(f"Training completion transaction successful: "
                              f"Job {job.id} -> COMPLETED, Training {training.id} -> TRAINED, "
                              f"Model {created_model.id} created")
                return True

        except Exception as e:
            self.logger.error(f"Error in training completion transaction for job {job.id}: {str(e)}", exc_info=True)
            return False
    
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
            'is_running': self.is_running,
            'poll_interval': self.poll_interval,
            'task_status': 'running' if self._task and not self._task.done() else 'stopped'
        }
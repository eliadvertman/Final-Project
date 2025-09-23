"""Training job monitoring service."""

import uuid
from datetime import datetime
from typing import List, Optional

from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.poller.base_job_monitor import BaseJobMonitor
from stroke_seg.dao.database import database
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.models import JobRecord, ModelRecord
from stroke_seg.dao.training_dao import TrainingDAO
from stroke_seg.logging_config import get_logger


class TrainingJobMonitor(BaseJobMonitor):
    """Job monitor specifically for training jobs."""

    def __init__(
        self,
        job_dao: Optional[JobDAO] = None,
        slurm_client: Optional[SlurmClient] = None,
        poll_interval: int = None
    ):
        """
        Initialize training job monitor.

        Args:
            job_dao: JobDAO instance (creates new one if None)
            slurm_client: SlurmClient instance (creates new one if None)
            poll_interval: Polling interval in seconds (default from env or 30)
        """
        super().__init__(job_dao, slurm_client, poll_interval, job_type='TRAINING')
        self.training_dao = TrainingDAO()
        self.model_dao = ModelDAO()
        self.logger = get_logger(__name__)

    def _get_jobs_to_monitor(self) -> List[JobRecord]:
        """Get list of training jobs to monitor."""
        # Get all active jobs and filter for training jobs
        all_active_jobs = self.job_dao.get_active_jobs()
        return [job for job in all_active_jobs if job.job_type == 'TRAINING']

    async def _handle_job_update(self, job: JobRecord, job_info: dict, current_status: str, new_status: str) -> bool:
        """
        Handle training job status update.

        Args:
            job: The job record to update
            job_info: Job information from SLURM
            current_status: Current job status
            new_status: New job status from SLURM

        Returns:
            True if update was successful, False otherwise
        """
        # Special handling for training job completion
        if new_status == 'COMPLETED':
            self.logger.info(f"Training job {job.id} completed, handling with transaction")
            return self._handle_training_completion(job, job_info)
        else:
            # Normal job update logic for non-completion states
            return self._handle_normal_update(job, job_info, new_status)

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

    def _handle_normal_update(self, job: JobRecord, job_info: dict, new_status: str) -> bool:
        """
        Handle normal job status updates (non-completion cases).

        Args:
            job: The job record to update
            job_info: Job information from SLURM
            new_status: New status from SLURM

        Returns:
            True if update was successful, False otherwise
        """
        try:
            start_time = job_info.get('start_time')
            end_time = job_info.get('end_time')
            error_message = job_info.get('error_message')
            slurm_state = job_info.get('state')

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
                self.logger.warning(f"Training job {job.id} failed: {error_message}")

            # Update job record in database
            job_uuid = uuid.UUID(job.id)
            updated_job = self.job_dao.update(job_uuid, **update_data)

            if updated_job:
                self.logger.debug(f"Training job {job.id} updated successfully to status: {new_status}")
                return True
            else:
                self.logger.error(f"Failed to update training job {job.id} in database")
                return False

        except Exception as e:
            self.logger.error(f"Error in normal training job update for {job.id}: {str(e)}", exc_info=True)
            return False
"""Evaluation job monitoring service."""

import uuid
from datetime import datetime
from typing import List, Optional

from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.poller.base_job_monitor import BaseJobMonitor
from stroke_seg.dao.database import database
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.models import JobRecord
from stroke_seg.dao.evaluation_dao import EvaluationDAO
from stroke_seg.logging_config import get_logger


class EvaluationJobMonitor(BaseJobMonitor):
    """Job monitor specifically for evaluation jobs."""

    def __init__(
        self,
        job_dao: Optional[JobDAO] = None,
        slurm_client: Optional[SlurmClient] = None,
        poll_interval: int = None
    ):
        """
        Initialize evaluation job monitor.

        Args:
            job_dao: JobDAO instance (creates new one if None)
            slurm_client: SlurmClient instance (creates new one if None)
            poll_interval: Polling interval in seconds (default from env or 30)
        """
        super().__init__(job_dao, slurm_client, poll_interval, job_type='EVALUATION')
        self.evaluation_dao = EvaluationDAO()
        self.logger = get_logger(__name__)

    def _get_jobs_to_monitor(self) -> List[JobRecord]:
        """Get list of evaluation jobs to monitor."""
        # Get all active jobs and filter for evaluation jobs
        all_active_jobs = self.job_dao.get_active_jobs()
        return [job for job in all_active_jobs if job.job_type == 'EVALUATION']

    async def _handle_job_update(self, job: JobRecord, job_info: dict, current_status: str, new_status: str) -> bool:
        """
        Handle evaluation job status update.

        Args:
            job: The job record to update
            job_info: Job information from SLURM
            current_status: Current job status
            new_status: New job status from SLURM

        Returns:
            True if update was successful, False otherwise
        """
        # Special handling for evaluation job completion
        if new_status == 'COMPLETED':
            self.logger.info(f"Evaluation job {job.id} completed, handling with transaction")
            return self._handle_evaluation_completion(job, job_info)
        elif new_status == 'FAILED':
            self.logger.info(f"Evaluation job {job.id} failed, handling with transaction")
            return self._handle_evaluation_failure(job, job_info)
        else:
            # Normal job update logic for non-terminal states
            return self._handle_normal_update(job, job_info, new_status)

    def _handle_evaluation_completion(self, job: JobRecord, job_info: dict) -> bool:
        """
        Handle evaluation job completion in a single transaction.
        Updates job status to COMPLETED and evaluation status to COMPLETED.

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

                # Find and update corresponding evaluation record
                evaluation = self.evaluation_dao.get_by_job_id(job_uuid)
                if not evaluation:
                    self.logger.error(f"No evaluation record found for completed job {job.id}")
                    return False

                evaluation_uuid = uuid.UUID(evaluation.id)
                evaluation_update_data = {'status': 'COMPLETED'}
                if end_time:
                    evaluation_update_data['end_time'] = end_time

                updated_evaluation = self.evaluation_dao.update(evaluation_uuid, **evaluation_update_data)
                if not updated_evaluation:
                    self.logger.error(f"Failed to update evaluation {evaluation.id} to COMPLETED")
                    return False

                self.logger.info(f"Evaluation completion transaction successful: "
                              f"Job {job.id} -> COMPLETED, Evaluation {evaluation.id} -> COMPLETED")
                return True

        except Exception as e:
            self.logger.error(f"Error in evaluation completion transaction for job {job.id}: {str(e)}", exc_info=True)
            return False

    def _handle_evaluation_failure(self, job: JobRecord, job_info: dict) -> bool:
        """
        Handle evaluation job failure in a single transaction.
        Updates job status to FAILED and evaluation status to FAILED.

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
            error_message = job_info.get('error_message')

            with database.atomic():
                # Update job record to FAILED
                job_update_data = {'status': 'FAILED'}
                if start_time and not job.start_time:
                    job_update_data['start_time'] = start_time
                if end_time and not job.end_time:
                    job_update_data['end_time'] = end_time
                if error_message:
                    job_update_data['error_message'] = error_message

                updated_job = self.job_dao.update(job_uuid, **job_update_data)
                if not updated_job:
                    self.logger.error(f"Failed to update job {job.id} to FAILED")
                    return False

                # Find and update corresponding evaluation record
                evaluation = self.evaluation_dao.get_by_job_id(job_uuid)
                if not evaluation:
                    self.logger.error(f"No evaluation record found for failed job {job.id}")
                    return False

                evaluation_uuid = uuid.UUID(evaluation.id)
                evaluation_update_data = {'status': 'FAILED'}
                if end_time:
                    evaluation_update_data['end_time'] = end_time
                if error_message:
                    evaluation_update_data['error_message'] = error_message

                updated_evaluation = self.evaluation_dao.update(evaluation_uuid, **evaluation_update_data)
                if not updated_evaluation:
                    self.logger.error(f"Failed to update evaluation {evaluation.id} to FAILED")
                    return False

                self.logger.info(f"Evaluation failure transaction successful: "
                              f"Job {job.id} -> FAILED, Evaluation {evaluation.id} -> FAILED")
                return True

        except Exception as e:
            self.logger.error(f"Error in evaluation failure transaction for job {job.id}: {str(e)}", exc_info=True)
            return False

    def _handle_normal_update(self, job: JobRecord, job_info: dict, new_status: str) -> bool:
        """
        Handle normal job status updates (non-terminal cases).

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

            # Update job record in database
            job_uuid = uuid.UUID(job.id)
            updated_job = self.job_dao.update(job_uuid, **update_data)

            if updated_job:
                # Also update evaluation record status if job is running
                if new_status == 'RUNNING':
                    evaluation = self.evaluation_dao.get_by_job_id(job_uuid)
                    if evaluation:
                        evaluation_uuid = uuid.UUID(evaluation.id)
                        self.evaluation_dao.update(evaluation_uuid, status='EVALUATING')
                        self.logger.debug(f"Updated evaluation {evaluation.id} to EVALUATING")

                self.logger.debug(f"Evaluation job {job.id} updated successfully to status: {new_status}")
                return True
            else:
                self.logger.error(f"Failed to update evaluation job {job.id} in database")
                return False

        except Exception as e:
            self.logger.error(f"Error in normal evaluation job update for {job.id}: {str(e)}", exc_info=True)
            return False

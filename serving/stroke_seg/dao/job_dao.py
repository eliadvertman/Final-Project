from typing import List, Optional
from peewee import DoesNotExist
from stroke_seg.dao.models import JobRecord
from datetime import datetime
import uuid

class JobDAO:
    """Data Access Object for JobRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, job_record: JobRecord) -> JobRecord:
        """Create a new job record."""
        job_record.save(force_insert=True)
        return job_record
    
    def get_by_id(self, job_uuid: uuid.UUID) -> Optional[JobRecord]:
        """Get a job by its UUID."""
        try:
            return JobRecord.get(JobRecord.id == str(job_uuid))
        except DoesNotExist:
            return None
    
    def get_for_training(self, training_record) -> Optional[JobRecord]:
        """Get the job for a specific training record."""
        if hasattr(training_record, 'job_id'):
            return training_record.job_id
        return None
    
    def get_by_sbatch_id(self, sbatch_id: str) -> Optional[JobRecord]:
        """Get a job by SLURM batch ID."""
        try:
            return JobRecord.get(JobRecord.sbatch_id == sbatch_id)
        except DoesNotExist:
            return None
    
    def get_by_status(self, status: str) -> List[JobRecord]:
        """Get all jobs with a specific status."""
        return list(JobRecord.select().where(JobRecord.status == status))
    
    def get_by_fold_and_task(self, fold_index: int, task_number: int) -> Optional[JobRecord]:
        """Get a job by fold index and task number."""
        try:
            return JobRecord.get(
                (JobRecord.fold_index == fold_index) &
                (JobRecord.task_number == task_number)
            )
        except DoesNotExist:
            return None
    
    def get_active_jobs(self) -> List[JobRecord]:
        """Get all jobs with PENDING or RUNNING status."""
        return list(JobRecord.select().where(JobRecord.status.in_(['PENDING', 'RUNNING'])))
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[JobRecord]:
        """Get all jobs with optional pagination."""
        query = JobRecord.select().order_by(JobRecord.start_time.desc(nulls='last')).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def update(self, job_uuid: uuid.UUID, **kwargs) -> Optional[JobRecord]:
        """Update a job record."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            for key, value in kwargs.items():
                setattr(job, key, value)
            job.save()
            return job
        except DoesNotExist:
            return None
    
    def delete(self, job_uuid: uuid.UUID) -> bool:
        """Delete a job record."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            job.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of jobs."""
        return JobRecord.select().count()
    
    def start_job(self, job_uuid: uuid.UUID) -> Optional[JobRecord]:
        """Start a job by updating status to RUNNING and setting start_time."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            job.status = 'RUNNING'
            job.start_time = datetime.now()
            job.save()
            return job
        except DoesNotExist:
            return None
    
    def complete_job(self, job_uuid: uuid.UUID) -> Optional[JobRecord]:
        """Complete a job by updating status to COMPLETED and setting end_time."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            job.status = 'COMPLETED'
            job.end_time = datetime.now()
            job.save()
            return job
        except DoesNotExist:
            return None
    
    def fail_job(self, job_uuid: uuid.UUID) -> Optional[JobRecord]:
        """Fail a job by updating status to FAILED and setting end_time."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            job.status = 'FAILED'
            job.end_time = datetime.now()
            job.save()
            return job
        except DoesNotExist:
            return None
    
    def update_status(self, job_uuid: uuid.UUID, status: str) -> Optional[JobRecord]:
        """Update job status with automatic timestamp management."""
        try:
            job = JobRecord.get(JobRecord.id == str(job_uuid))
            job.status = status
            
            if status == 'RUNNING' and job.start_time is None:
                job.start_time = datetime.now()
            elif status in ['COMPLETED', 'FAILED'] and job.end_time is None:
                job.end_time = datetime.now()
            
            job.save()
            return job
        except DoesNotExist:
            return None
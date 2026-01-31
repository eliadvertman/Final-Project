"""Data Access Object for EvaluationRecord operations."""

from typing import List, Optional
from peewee import DoesNotExist
from stroke_seg.dao.models import EvaluationRecord
import uuid


class EvaluationDAO:
    """Data Access Object for EvaluationRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, evaluation_record: EvaluationRecord) -> EvaluationRecord:
        """Create a new evaluation record."""
        evaluation_record.save(force_insert=True)
        return evaluation_record
    
    def get_by_id(self, evaluation_uuid: uuid.UUID) -> Optional[EvaluationRecord]:
        """Get an evaluation by its UUID."""
        try:
            return EvaluationRecord.get(EvaluationRecord.id == str(evaluation_uuid))
        except DoesNotExist:
            return None
    
    def get_by_job_id(self, job_uuid: uuid.UUID) -> Optional[EvaluationRecord]:
        """Get an evaluation by its job_id."""
        try:
            return EvaluationRecord.get(EvaluationRecord.job_id == str(job_uuid))
        except DoesNotExist:
            return None
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[EvaluationRecord]:
        """Get all evaluations with optional pagination."""
        query = EvaluationRecord.select().order_by(EvaluationRecord.created_at.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_status(self, status: str) -> List[EvaluationRecord]:
        """Get all evaluations with a specific status."""
        return list(EvaluationRecord.select().where(EvaluationRecord.status == status))
    
    def update(self, evaluation_uuid: uuid.UUID, **kwargs) -> Optional[EvaluationRecord]:
        """Update an evaluation record."""
        try:
            evaluation = EvaluationRecord.get(EvaluationRecord.id == str(evaluation_uuid))
            for key, value in kwargs.items():
                setattr(evaluation, key, value)
            evaluation.save()
            return evaluation
        except DoesNotExist:
            return None
    
    def delete(self, evaluation_uuid: uuid.UUID) -> bool:
        """Delete an evaluation record."""
        try:
            evaluation = EvaluationRecord.get(EvaluationRecord.id == str(evaluation_uuid))
            evaluation.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of evaluations."""
        return EvaluationRecord.select().count()
    
    def get_job_for_evaluation(self, evaluation_uuid: uuid.UUID) -> Optional['JobRecord']:
        """Get the job record associated with an evaluation."""
        evaluation = self.get_by_id(evaluation_uuid)
        return evaluation.job_id if evaluation else None




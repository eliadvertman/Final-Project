import uuid
from typing import List, Optional

from peewee import DoesNotExist

from stroke_seg.dao.models import InferenceRecord


class InferenceDAO:
    """Data Access Object for InferenceRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, inference_record: InferenceRecord) -> InferenceRecord:
        """Create a new inference record."""
        return inference_record.save(force_insert=True)
    
    
    def get_by_predict_id(self, predict_uuid: uuid.UUID) -> Optional[InferenceRecord]:
        """Get an inference by predict_id UUID."""
        try:
            return InferenceRecord.get(InferenceRecord.predict_id == str(predict_uuid))
        except DoesNotExist:
            return None
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[InferenceRecord]:
        """Get all inferences with optional pagination."""
        query = InferenceRecord.select().order_by(InferenceRecord.created_at.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_model_id(self, model_uuid: uuid.UUID) -> List[InferenceRecord]:
        """Get all inferences for a specific model."""
        return list(InferenceRecord.select().where(InferenceRecord.model_id == str(model_uuid)))
    
    def get_by_status(self, status: str) -> List[InferenceRecord]:
        """Get all inferences with a specific status."""
        return list(InferenceRecord.select().where(InferenceRecord.status == status))
    
    def update(self, predict_uuid: uuid.UUID, **kwargs) -> Optional[InferenceRecord]:
        """Update an inference record."""
        try:
            inference = InferenceRecord.get(InferenceRecord.predict_id == str(predict_uuid))
            for key, value in kwargs.items():
                setattr(inference, key, value)
            inference.save()
            return inference
        except DoesNotExist:
            return None
    
    def delete(self, predict_uuid: uuid.UUID) -> bool:
        """Delete an inference record."""
        try:
            inference = InferenceRecord.get(InferenceRecord.predict_id == str(predict_uuid))
            inference.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of inferences."""
        return InferenceRecord.select().count()
    
    def count_by_model(self, model_uuid: uuid.UUID) -> int:
        """Get count of inferences for a specific model."""
        return InferenceRecord.select().where(InferenceRecord.model_id == str(model_uuid)).count()
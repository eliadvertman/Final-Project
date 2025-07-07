from typing import List, Optional
from peewee import DoesNotExist
from .models import InferenceRecord, ModelRecord
from .database import connect_db

class InferenceDAO:
    """Data Access Object for InferenceRecord operations."""
    
    def __init__(self):
        """Initialize DAO and ensure database connection."""
        connect_db()
    
    def create(self, status: str, model_id: Optional[int] = None, batch_id: Optional[str] = None,
               input_path: Optional[str] = None, output_path: Optional[str] = None) -> InferenceRecord:
        """Create a new inference record."""
        inference = InferenceRecord.create(
            model_id=model_id,
            batch_id=batch_id,
            input_path=input_path,
            output_path=output_path,
            status=status
        )
        return inference
    
    def get_by_id(self, inference_id: int) -> Optional[InferenceRecord]:
        """Get an inference by ID."""
        try:
            return InferenceRecord.get_by_id(inference_id)
        except DoesNotExist:
            return None
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[InferenceRecord]:
        """Get all inferences with optional pagination."""
        query = InferenceRecord.select().offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_model_id(self, model_id: int) -> List[InferenceRecord]:
        """Get all inferences for a specific model."""
        return list(InferenceRecord.select().where(InferenceRecord.model_id == model_id))
    
    def get_by_status(self, status: str) -> List[InferenceRecord]:
        """Get all inferences with a specific status."""
        return list(InferenceRecord.select().where(InferenceRecord.status == status))
    
    def get_by_batch_id(self, batch_id: str) -> List[InferenceRecord]:
        """Get all inferences with a specific batch ID."""
        return list(InferenceRecord.select().where(InferenceRecord.batch_id == batch_id))
    
    def update(self, inference_id: int, **kwargs) -> Optional[InferenceRecord]:
        """Update an inference record."""
        try:
            inference = InferenceRecord.get_by_id(inference_id)
            for key, value in kwargs.items():
                setattr(inference, key, value)
            inference.save()
            return inference
        except DoesNotExist:
            return None
    
    def delete(self, inference_id: int) -> bool:
        """Delete an inference record."""
        try:
            inference = InferenceRecord.get_by_id(inference_id)
            inference.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of inferences."""
        return InferenceRecord.select().count()
    
    def count_by_model(self, model_id: int) -> int:
        """Get count of inferences for a specific model."""
        return InferenceRecord.select().where(InferenceRecord.model_id == model_id).count()
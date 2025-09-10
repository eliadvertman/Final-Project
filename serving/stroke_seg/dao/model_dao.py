from typing import List, Optional
from peewee import DoesNotExist
from stroke_seg.dao.models import ModelRecord
import uuid

class ModelDAO:
    """Data Access Object for ModelRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, model_record: ModelRecord) -> ModelRecord:
        """Create a new model record."""
        model_record.save(force_insert=True)
        return model_record
    
    def get_by_id(self, model_uuid: uuid.UUID) -> Optional[ModelRecord]:
        """Get a model by its UUID."""
        try:
            return ModelRecord.get(ModelRecord.id == str(model_uuid))
        except DoesNotExist:
            return None
    
    def get_by_training_id(self, training_uuid: uuid.UUID) -> List[ModelRecord]:
        """Get all models for a specific training."""
        return list(ModelRecord.select().where(ModelRecord.training_id == str(training_uuid)))
    
    def get_by_name(self, model_name: str) -> Optional[ModelRecord]:
        """Get a model by name."""
        try:
            return ModelRecord.get(ModelRecord.model_name == model_name)
        except DoesNotExist:
            return None
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelRecord]:
        """Get all models with optional pagination."""
        query = ModelRecord.select().order_by(ModelRecord.created_at.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def update(self, model_uuid: uuid.UUID, **kwargs) -> Optional[ModelRecord]:
        """Update a model record."""
        try:
            model = ModelRecord.get(ModelRecord.id == str(model_uuid))
            for key, value in kwargs.items():
                setattr(model, key, value)
            model.save()
            return model
        except DoesNotExist:
            return None
    
    def delete(self, model_uuid: uuid.UUID) -> bool:
        """Delete a model record."""
        try:
            model = ModelRecord.get(ModelRecord.id == str(model_uuid))
            model.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of models."""
        return ModelRecord.select().count()
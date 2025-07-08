from typing import List, Optional
from peewee import DoesNotExist
from .models import ModelRecord
import uuid

class ModelDAO:
    """Data Access Object for ModelRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, model_record: ModelRecord) -> ModelRecord:
        """Create a new model record."""
        model_record.save()
        return model_record
    
    
    def get_by_model_id(self, model_uuid: uuid.UUID) -> Optional[ModelRecord]:
        """Get a model by model_id UUID."""
        try:
            return ModelRecord.get(ModelRecord.model_id == str(model_uuid))
        except DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional[ModelRecord]:
        """Get a model by name."""
        try:
            return ModelRecord.get(ModelRecord.name == name)
        except DoesNotExist:
            return None
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelRecord]:
        """Get all models with optional pagination."""
        query = ModelRecord.select().order_by(ModelRecord.created_at.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_status(self, status: str) -> List[ModelRecord]:
        """Get all models with a specific status."""
        return list(ModelRecord.select().where(ModelRecord.status == status))
    
    def update(self, model_uuid: uuid.UUID, **kwargs) -> Optional[ModelRecord]:
        """Update a model record."""
        try:
            model = ModelRecord.get(ModelRecord.model_id == str(model_uuid))
            for key, value in kwargs.items():
                setattr(model, key, value)
            model.save()
            return model
        except DoesNotExist:
            return None
    
    def delete(self, model_uuid: uuid.UUID) -> bool:
        """Delete a model record."""
        try:
            model = ModelRecord.get(ModelRecord.model_id == str(model_uuid))
            model.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of models."""
        return ModelRecord.select().count()
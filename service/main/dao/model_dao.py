from typing import List, Optional
from peewee import DoesNotExist
from .models import ModelRecord
from .database import connect_db

class ModelDAO:
    """Data Access Object for ModelRecord operations."""
    
    def __init__(self):
        """Initialize DAO and ensure database connection."""
        connect_db()
    
    def create(self, name: str, status: str, batch_id: Optional[str] = None, 
               input_path: Optional[str] = None, output_path: Optional[str] = None) -> ModelRecord:
        """Create a new model record."""
        model = ModelRecord.create(
            name=name,
            batch_id=batch_id,
            input_path=input_path,
            output_path=output_path,
            status=status
        )
        return model
    
    def get_by_id(self, model_id: int) -> Optional[ModelRecord]:
        """Get a model by ID."""
        try:
            return ModelRecord.get_by_id(model_id)
        except DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional[ModelRecord]:
        """Get a model by name."""
        try:
            return ModelRecord.get(ModelRecord.name == name)
        except DoesNotExist:
            return None
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelRecord]:
        """Get all models with optional pagination."""
        query = ModelRecord.select().offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_status(self, status: str) -> List[ModelRecord]:
        """Get all models with a specific status."""
        return list(ModelRecord.select().where(ModelRecord.status == status))
    
    def update(self, model_id: int, **kwargs) -> Optional[ModelRecord]:
        """Update a model record."""
        try:
            model = ModelRecord.get_by_id(model_id)
            for key, value in kwargs.items():
                setattr(model, key, value)
            model.save()
            return model
        except DoesNotExist:
            return None
    
    def delete(self, model_id: int) -> bool:
        """Delete a model record."""
        try:
            model = ModelRecord.get_by_id(model_id)
            model.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of models."""
        return ModelRecord.select().count()
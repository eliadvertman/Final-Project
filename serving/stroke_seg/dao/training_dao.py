from typing import List, Optional
from peewee import DoesNotExist
from stroke_seg.dao.models import TrainingRecord
import uuid

class TrainingDAO:
    """Data Access Object for ModelRecord operations."""
    
    def __init__(self):
        """Initialize DAO."""
        pass
    
    def create(self, training_record: TrainingRecord) -> TrainingRecord:
        """Create a new model record."""
        return training_record.save(force_insert=True)
    
    
    def get_by_id(self, training_uuid: uuid.UUID) -> Optional[TrainingRecord]:
        """Get a training by its UUID."""
        try:
            return TrainingRecord.get(TrainingRecord.id == str(training_uuid))
        except DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional[TrainingRecord]:
        """Get a model by name."""
        try:
            return TrainingRecord.get(TrainingRecord.name == name)
        except DoesNotExist:
            return None
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[TrainingRecord]:
        """Get all trainings with optional pagination."""
        query = TrainingRecord.select().order_by(TrainingRecord.id.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_by_status(self, status: str) -> List[TrainingRecord]:
        """Get all trainings with a specific status."""
        return list(TrainingRecord.select().where(TrainingRecord.status == status))
    
    def update(self, training_uuid: uuid.UUID, **kwargs) -> Optional[TrainingRecord]:
        """Update a training record."""
        try:
            training = TrainingRecord.get(TrainingRecord.id == str(training_uuid))
            for key, value in kwargs.items():
                setattr(training, key, value)
            training.save()
            return training
        except DoesNotExist:
            return None
    
    def delete(self, training_uuid: uuid.UUID) -> bool:
        """Delete a training record."""
        try:
            training = TrainingRecord.get(TrainingRecord.id == str(training_uuid))
            training.delete_instance()
            return True
        except DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total count of trainings."""
        return TrainingRecord.select().count()
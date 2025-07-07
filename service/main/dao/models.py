from peewee import *
from datetime import datetime
from .database import BaseModel

class ModelRecord(BaseModel):
    """ORM model for the models table."""
    id = AutoField(primary_key=True)
    name = CharField(max_length=255, null=False)
    batch_id = CharField(max_length=255, null=True)
    input_path = CharField(max_length=500, null=True)
    output_path = CharField(max_length=500, null=True)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('TRAINING', 'SERVING', 'DELETED', 'INVALID')")])
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'models'
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class InferenceRecord(BaseModel):
    """ORM model for the inference table."""
    id = AutoField(primary_key=True)
    model_id = ForeignKeyField(ModelRecord, backref='inferences', null=True)
    batch_id = CharField(max_length=255, null=True)
    input_path = CharField(max_length=500, null=True)
    output_path = CharField(max_length=500, null=True)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('COMPLETED', 'RUNNING', 'FAILED')")])
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'inference'
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
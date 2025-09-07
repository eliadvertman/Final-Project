from peewee import *
from playhouse.postgres_ext import JSONField
from datetime import datetime
import uuid
from stroke_seg.dao.database import BaseModel

class ModelRecord(BaseModel):
    """ORM model for the models table."""
    model_id = CharField(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    name = CharField(max_length=255, null=False)
    images_path = CharField(max_length=500, null=True)
    labels_path = CharField(max_length=500, null=True)
    dataset_path = CharField(max_length=500, null=True)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('PENDING', 'TRAINING', 'TRAINED', 'FAILED', 'DEPLOYED')")])
    progress = FloatField(default=0.0)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    error_message = TextField(null=True)
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
    predict_id = CharField(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    model_id = ForeignKeyField(ModelRecord, field='model_id', backref='inferences', null=False)
    input_data = JSONField(null=False)
    prediction = JSONField(null=True)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')")])
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    error_message = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'inference'
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
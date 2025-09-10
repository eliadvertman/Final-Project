from peewee import *
from playhouse.postgres_ext import JSONField
from datetime import datetime
import uuid

from stroke_seg.dao.database import BaseModel


class TrainingRecord(BaseModel):
    """ORM model for the training table."""
    id = CharField(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    name = CharField(max_length=255, null=False)
    images_path = CharField(max_length=500, null=True)
    labels_path = CharField(max_length=500, null=True)
    status = CharField(max_length=20, null=False, constraints=[Check("status IN ('TRAINING', 'TRAINED', 'FAILED')")])
    progress = FloatField(default=0.0)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    error_message = TextField(null=True)
    
    class Meta:
        table_name = 'training'


class ModelRecord(BaseModel):
    """ORM model for the model table."""
    id = CharField(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    training_id = ForeignKeyField(TrainingRecord, field='id', backref='models', null=False)
    model_name = CharField(max_length=255, null=False)
    model_path = CharField(max_length=500, null=True)
    created_at = DateTimeField(null=True)
    
    class Meta:
        table_name = 'model'


class InferenceRecord(BaseModel):
    """ORM model for the inference table."""
    predict_id = CharField(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    model_id = ForeignKeyField(ModelRecord, field='id', backref='inferences', null=False)
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
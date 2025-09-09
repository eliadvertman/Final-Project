"""Pydantic models for API request and response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class TrainingConfig(BaseModel):
    """Request model for training configuration."""
    
    model_name: str = Field(None, alias="modelName", description="A unique name for the new model")
    images_path: Optional[str] = Field(None, alias="imagesPath", description="Path to raw images data")
    labels_path: Optional[str] = Field(None, alias="labelsPath", description="Path to raw labels data")
    dataset_path: Optional[str] = Field(None, alias="datasetPath", description="Path to dataset")

class InferenceInput(BaseModel):
    model_id: str = Field(None, alias="modelId")
    input_path: str = Field(None, alias="inputPath")

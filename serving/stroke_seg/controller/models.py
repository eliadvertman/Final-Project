"""Pydantic models for API request and response validation."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


ConfigurationType = Literal["2d", "3d_fullres", "3d_lowres", "3d_cascade_lowres"]


class TrainingConfig(BaseModel):
    """Request model for training configuration."""

    model_name: str = Field(None, alias="modelName", description="A unique name for the new model")
    images_path: Optional[str] = Field(None, alias="imagesPath", description="Path to raw images data")
    labels_path: Optional[str] = Field(None, alias="labelsPath", description="Path to raw labels data")
    configuration: ConfigurationType = Field(..., description="nnUNet configuration type (2d, 3d_fullres, 3d_lowres, 3d_cascade_lowres)")

class InferenceInput(BaseModel):
    model_id: str = Field(None, alias="modelId")
    input_path: str = Field(None, alias="inputPath")
    fold_index: int = Field(None, alias="foldIndex", description="Fold index for cross-validation")

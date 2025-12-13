"""Template variables dataclass for sbatch template interpolation."""
import time
from dataclasses import dataclass
from typing import Dict, Any
from stroke_seg.config import task_number


@dataclass
class TrainingTemplateVariables:
    """Variables required for sbatch template interpolation."""

    model_name: str
    model_path: str
    configuration: str
    timestamp: time = time.time()

    def __post_init__(self):
        """Validate the template variables after initialization."""
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError("model_name must be a non-empty string")
        if not self.model_path or not isinstance(self.model_path, str):
            raise ValueError("model_path must be a non-empty string")
        valid_configurations = ["2d", "3d_fullres", "3d_lowres", "3d_cascade_lowres"]
        if not self.configuration or self.configuration not in valid_configurations:
            raise ValueError(f"configuration must be one of: {valid_configurations}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dataclass to dictionary for template formatting.

        Returns:
            Dictionary representation of template variables
        """
        return {
            'model_name': self.model_name,
            'model_path': self.model_path,
            'timestamp': self.timestamp,
            'configuration': self.configuration,
            'task_number': task_number
        }


@dataclass
class PredictionTemplateVariables:
    """Variables required for prediction sbatch template interpolation."""

    input_path: str
    model_name: str
    model_path: str
    output_path: str
    fold_index: int
    timestamp: float = time.time()

    def __post_init__(self):
        """Validate the template variables after initialization."""
        if not self.input_path or not isinstance(self.input_path, str):
            raise ValueError("input_path must be a non-emty string")
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError("model_name must be a non-empty string")
        if not self.model_path or not isinstance(self.model_path, str):
            raise ValueError("model_path must be a non-empty string")
        if not self.output_path or not isinstance(self.output_path, str):
            raise ValueError("output_path must be a non-empty string")
        if self.fold_index is None or not isinstance(self.fold_index, int):
            raise ValueError("fold_index must be an integer")


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dataclass to dictionary for template formatting.

        Returns:
            Dictionary representation of template variables
        """
        return {
            'input_path' : self.input_path,
            'model_name': self.model_name,
            'model_path': self.model_path,
            'output_path': self.output_path,
            'fold_index': self.fold_index,
            'timestamp': self.timestamp
        }
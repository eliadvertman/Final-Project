"""Template variables dataclass for sbatch template interpolation."""
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class TrainingTemplateVariables:
    """Variables required for sbatch template interpolation."""
    
    model_name: str
    model_path:str
    fold_index: int
    task_number: int
    timestamp: time = time.time()

    def __post_init__(self):
        """Validate the template variables after initialization."""
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError("model_name must be a non-empty string")
        if not self.model_path or not isinstance(self.model_path, str):
            raise ValueError("model_path must be a non-empty string")
        if not self.fold_index or not isinstance(self.fold_index, int):
            raise ValueError("fold_index must be a non-empty string")
        if not self.task_number or not isinstance(self.task_number, int):
            raise ValueError("task_number must be a non-empty string")

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
            'fold_index': self.fold_index,
            'task_number': self.task_number
        }


@dataclass
class PredictionTemplateVariables:
    """Variables required for prediction sbatch template interpolation."""

    model_name: str
    model_path: str
    output_path: str
    timestamp: float = time.time()

    def __post_init__(self):
        """Validate the template variables after initialization."""
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError("model_name must be a non-empty string")
        if not self.model_path or not isinstance(self.model_path, str):
            raise ValueError("model_path must be a non-empty string")
        if not self.output_path or not isinstance(self.output_path, str):
            raise ValueError("output_path must be a non-empty string")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dataclass to dictionary for template formatting.

        Returns:
            Dictionary representation of template variables
        """
        return {
            'model_name': self.model_name,
            'model_path': self.model_path,
            'output_path': self.output_path,
            'timestamp': self.timestamp
        }
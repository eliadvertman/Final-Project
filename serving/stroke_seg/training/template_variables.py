"""Template variables dataclass for sbatch template interpolation."""
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class SbatchTemplateVariables:
    """Variables required for sbatch template interpolation."""
    
    model_name: str
    fold_index: int
    task_number: int
    timestamp: time = time.time()

    def __post_init__(self):
        """Validate the template variables after initialization."""
        if not self.model_name or not isinstance(self.model_name, str):
            raise ValueError("model_name must be a non-empty string")
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
            'timestamp': self.timestamp,
            'fold_index': self.fold_index,
            'task_number': self.task_number
        }
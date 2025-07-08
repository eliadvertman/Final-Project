"""Controller package for the ML prediction service."""

from .model_controller import model_bp
from .prediction_controller import prediction_bp

__all__ = ['model_bp', 'prediction_bp']
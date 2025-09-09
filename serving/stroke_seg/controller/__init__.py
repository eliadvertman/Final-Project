"""Controller package for the ML prediction service."""

from stroke_seg.controller.model_controller import model_bp
from stroke_seg.controller.prediction_controller import prediction_bp

__all__ = ['model_bp', 'prediction_bp']
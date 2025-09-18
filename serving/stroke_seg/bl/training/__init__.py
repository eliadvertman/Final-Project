"""Singularity package for model training operations."""

from stroke_seg.bl.client.bash.bash_client import BashClient
from stroke_seg.bl.template.template_variables import TrainingTemplateVariables

__all__ = ['TemplateGenerator', 'BashClient', 'SbatchClient', 'TrainingTemplateVariables']
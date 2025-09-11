"""Singularity package for model training operations."""


from .template_generator import TemplateGenerator
from .bash_client import BashClient
from .sbatch_client import SbatchClient
from .template_variables import SbatchTemplateVariables

__all__ = ['TemplateGenerator', 'BashClient', 'SbatchClient', 'SbatchTemplateVariables']
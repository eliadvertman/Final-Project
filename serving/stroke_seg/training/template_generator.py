"""Template generator for sbatch files."""

import re
from pathlib import Path

from stroke_seg.logging_config import get_logger
from stroke_seg.exceptions import ModelCreationException
from .template_variables import SbatchTemplateVariables


class TemplateGenerator:
    """Handles sbatch template loading and variable interpolation."""
    
    def __init__(self, template_path: str = None):
        """
        Initialize the template generator.
        
        Args:
            template_path: Path to sbatch template file
        """
        self.logger = get_logger(__name__)
        template_path = template_path or self._get_default_template_path()
        self.template_content = self._load_template(template_path)
        
    def _get_default_template_path(self) -> str:
        """Get the default template path."""
        current_dir = Path(__file__).parent.parent
        template_path = current_dir / "templates" / "sbatch_train_template"
        return str(template_path)
    
    def _load_template(self, template_path : str) -> str:
        """
        Load the sbatch template file.
        
        Returns:
            Template content as string
            
        Raises:
            ModelCreationException: If template file cannot be read
        """
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            self.logger.debug(f"Template loaded successfully from: {template_path}")
            return template_content
            
        except FileNotFoundError:
            error_msg = f"Template file not found: {template_path}"
            self.logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"Failed to load template: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    def interpolate_template(self, variables: SbatchTemplateVariables) -> str:
        """
        Interpolate variables into the template.
        
        Args:
            variables: Template variables dataclass
            
        Returns:
            Interpolated template content
            
        Raises:
            ModelCreationException: If template interpolation fails
        """
        try:
            # Convert dataclass to dict for formatting
            variables_dict = variables.to_dict()
            
            # Find all placeholders in template
            placeholders = re.findall(r'\{([^}]+)\}', self.template_content)
            
            # Check if all required variables are provided
            missing_vars = [var for var in placeholders if var not in variables_dict]
            if missing_vars:
                error_msg = f"Missing template variables: {missing_vars}"
                self.logger.error(error_msg)
                raise
            
            # Interpolate variables
            interpolated = self.template_content.format(**variables_dict)
            
            self.logger.debug(
                f"Template interpolated successfully with variables: {list(variables_dict.keys())}"
            )
            return interpolated
            
        except KeyError as e:
            error_msg = f"Template variable not found: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        except Exception as e:
            error_msg = f"Template interpolation failed: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
    
    def generate_sbatch_content(self, variables: SbatchTemplateVariables) -> str:
        """
        Generate sbatch content by interpolating variables into loaded template.
        
        Args:
            variables: Template variables dataclass
            
        Returns:
            Interpolated sbatch content
            
        Raises:
            ModelCreationException: If template generation fails
        """
        variables_dict = variables.to_dict()
        self.logger.debug(f"Generating sbatch content with variables: {list(variables_dict.keys())}")
        
        sbatch_content = self.interpolate_template(variables)
        
        self.logger.info("Sbatch content generated successfully")
        self.logger.debug(f"Sbatch content is {sbatch_content}")
        return sbatch_content
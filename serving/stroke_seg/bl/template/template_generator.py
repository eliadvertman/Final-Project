"""Template generator for sbatch files."""

import re
import traceback
from pathlib import Path

from stroke_seg.logging_config import get_logger
from stroke_seg.exceptions import ModelCreationException
from .template_variables import TrainingTemplateVariables, PredictionTemplateVariables, EvaluationTemplateVariables


class TemplateGenerator:
    """Handles sbatch template loading and variable interpolation."""
    
    def __init__(self, template_path: str):
        """
        Initialize the template generator.

        Args:
            template_path: Path to sbatch template file (required)

        Raises:
            ValueError: If template_path is None or empty
            FileNotFoundError: If template file doesn't exist
        """
        if not template_path:
            raise ValueError("template_path is required")

        self.logger = get_logger(__name__)
        self.template_content = self._load_template(template_path)

    def _load_template(self, template_path : str) -> str:
        """
        Load the sbatch template file.

        Args:
            template_path: Path to the template file

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
            ModelCreationException: If template file cannot be read
        """
        if not Path(template_path).is_file():
            error_msg = f"Template file not found: {template_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(template_path, 'r') as f:
                template_content = f.read()

            self.logger.debug(f"Template loaded successfully from: {template_path}")
            return template_content

        except Exception as e:
            error_msg = f"Failed to load template: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
    
    def interpolate_template(self, variables: TrainingTemplateVariables) -> str:
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
            self.logger.error(traceback.format_exc())
            raise ModelCreationException(error_msg)
        except Exception as e:
            error_msg = f"Template interpolation failed: {str(e)}"
            self.logger.error(traceback.format_exc())
            raise ModelCreationException(error_msg)
    
    def generate_training_sbatch_content(self, variables: TrainingTemplateVariables) -> str:
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

    def generate_inference_sbatch_content(self, variables: PredictionTemplateVariables) -> str:
        """
        Generate sbatch content for inference by interpolating variables into loaded template.

        Args:
            variables: Prediction template variables dataclass

        Returns:
            Interpolated sbatch content for inference

        Raises:
            ModelCreationException: If template generation fails
        """
        variables_dict = variables.to_dict()
        self.logger.debug(f"Generating inference sbatch content with variables: {list(variables_dict.keys())}")

        try:
            # Find all placeholders in template
            placeholders = re.findall(r'\{([^}]+)\}', self.template_content)

            # Check if all required variables are provided
            missing_vars = [var for var in placeholders if var not in variables_dict]
            if missing_vars:
                error_msg = f"Missing template variables: {missing_vars}"
                self.logger.error(error_msg)
                raise ModelCreationException(error_msg)

            # Interpolate variables
            sbatch_content = self.template_content.format(**variables_dict)

            self.logger.info("Inference sbatch content generated successfully")
            self.logger.debug(f"Inference sbatch content is {sbatch_content}")
            return sbatch_content

        except KeyError as e:
            error_msg = f"Template variable not found: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        except Exception as e:
            error_msg = f"Inference template generation failed: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)

    def generate_evaluation_sbatch_content(self, variables: EvaluationTemplateVariables) -> str:
        """
        Generate sbatch content for evaluation by interpolating variables into loaded template.

        Args:
            variables: Evaluation template variables dataclass

        Returns:
            Interpolated sbatch content for evaluation

        Raises:
            ModelCreationException: If template generation fails
        """
        variables_dict = variables.to_dict()
        self.logger.debug(f"Generating evaluation sbatch content with variables: {list(variables_dict.keys())}")

        try:
            # Find all placeholders in template
            placeholders = re.findall(r'\{([^}]+)\}', self.template_content)

            # Check if all required variables are provided
            missing_vars = [var for var in placeholders if var not in variables_dict]
            if missing_vars:
                error_msg = f"Missing template variables: {missing_vars}"
                self.logger.error(error_msg)
                raise ModelCreationException(error_msg)

            # Interpolate variables
            sbatch_content = self.template_content.format(**variables_dict)

            self.logger.info("Evaluation sbatch content generated successfully")
            self.logger.debug(f"Evaluation sbatch content is {sbatch_content}")
            return sbatch_content

        except KeyError as e:
            error_msg = f"Template variable not found: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        except Exception as e:
            error_msg = f"Evaluation template generation failed: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
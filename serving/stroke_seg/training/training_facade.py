"""Singularity interface facade for model training operations."""

from stroke_seg.logging_config import get_logger
from stroke_seg.exceptions import ModelCreationException
from .template_generator import TemplateGenerator
from .sbatch_client import SbatchClient
from .template_variables import SbatchTemplateVariables


class ModelTrainingFacade:
    """Facade interface for interacting with Singularity for model training."""
    
    def __init__(self, template_path: str = None):
        """
        Initialize the Singularity interface.
        
        Args:
            template_path: Path to sbatch template file
        """
        self.logger = get_logger(__name__)
        self.template_generator = TemplateGenerator(template_path)
        self.sbatch_client = SbatchClient()
        
    def submit_training_job(self, training_variables: SbatchTemplateVariables) -> str:
        """
        Submit a training job using sbatch.
        
        Args:
            training_variables: Template variables dataclass containing model_name and model_id
            
        Returns:
            Batch job ID as string
            
        Raises:
            ModelCreationException: If job submission fails at any step
        """
        variables_dict = training_variables.to_dict()
        self.logger.info(
            f"Submitting training job with variables: {list(variables_dict.keys())}"
        )
        
        try:
            # Generate sbatch content using template generator
            sbatch_content = self.template_generator.generate_sbatch_content(training_variables)
            
            # Submit job using sbatch client
            job_id = self.sbatch_client.submit_sbatch_job(sbatch_content)
            
            self.logger.info(f"Training job submitted successfully - Job ID: {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit training job: {str(e)}")
            raise
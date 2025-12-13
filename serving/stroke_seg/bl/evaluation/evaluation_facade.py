"""Singularity interface facade for model evaluation operations."""
from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.client.fs.fs_client import create_dir
from stroke_seg.logging_config import get_logger
from stroke_seg.bl.template.template_generator import TemplateGenerator
from stroke_seg.bl.template.template_variables import EvaluationTemplateVariables


class EvaluationFacade:
    """Facade interface for interacting with Singularity for model evaluation."""

    def __init__(self, template_path: str = None):
        """
        Initialize the Singularity interface.
        
        Args:
            template_path: Path to sbatch template file
        """
        self.logger = get_logger(__name__)
        self.template_generator = TemplateGenerator(template_path)
        self.sbatch_client = SlurmClient()
        
    def submit_evaluation_job(self, evaluation_variables: EvaluationTemplateVariables) -> tuple[str, str]:
        """
        Submit an evaluation job using sbatch.

        Args:
            evaluation_variables: Template variables dataclass containing evaluation parameters

        Returns:
            Tuple of (batch_job_id, sbatch_content) as strings

        Raises:
            ModelCreationException: If job submission fails at any step
        """
        variables_dict = evaluation_variables.to_dict()
        self.logger.info(
            f"Submitting evaluation job with variables: {list(variables_dict.keys())}"
        )
        
        try:
            # Create output_path directory for evaluation results
            create_dir(evaluation_variables.output_path)

            # Generate sbatch content using template generator
            sbatch_content = self.template_generator.generate_evaluation_sbatch_content(evaluation_variables)
            
            # Submit job using sbatch client
            job_id = self.sbatch_client.submit_sbatch_job(sbatch_content)

            self.logger.info(f"Evaluation job submitted successfully - Job ID: {job_id}")
            return job_id, sbatch_content
            
        except Exception as e:
            self.logger.error(f"Failed to submit evaluation job: {str(e)}")
            raise


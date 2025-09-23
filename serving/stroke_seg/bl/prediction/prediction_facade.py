"""Singularity interface facade for prediction operations."""

from stroke_seg.logging_config import get_logger
from stroke_seg.bl.template.template_generator import TemplateGenerator
from stroke_seg.bl.client.slurm.slurm_client import SlurmClient
from stroke_seg.bl.template.template_variables import PredictionTemplateVariables

from stroke_seg.bl.client.fs.fs_client import create_dir


class PredictionFacade:
    """Facade interface for interacting with Singularity for predictions."""

    def __init__(self, template_path: str = None):
        """
        Initialize the Singularity interface.

        Args:
            template_path: Path to sbatch template file
        """
        self.logger = get_logger(__name__)
        self.template_generator = TemplateGenerator(template_path)
        self.slurm_client = SlurmClient()

    def submit_prediction_job(self, prediction_variables: PredictionTemplateVariables) -> tuple[str, str]:
        """
        Submit a prediction job using sbatch.

        Args:
            prediction_variables: Template variables dataclass containing model_id and input_path

        Returns:
            Tuple of (batch_job_id, sbatch_content) as strings

        Raises:
            ModelCreationException: If job submission fails at any step
        """
        variables_dict = prediction_variables.to_dict()
        self.logger.info(
            f"Submitting prediction job with variables: {list(variables_dict.keys())}"
        )

        try:
            # Create output_path directory
            create_dir(prediction_variables.output_path)

            # Generate sbatch content using template generator
            sbatch_content = self.template_generator.generate_inference_sbatch_content(prediction_variables)

            # Submit job using sbatch client
            job_id = self.slurm_client.submit_sbatch_job(sbatch_content)

            self.logger.info(f"Prediction job submitted successfully - Job ID: {job_id}")
            return job_id, sbatch_content

        except Exception as e:
            self.logger.error(f"Failed to submit prediction job: {str(e)}")
            raise
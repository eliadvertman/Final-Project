"""Sbatch client for SLURM job submission operations."""

import re
from typing import Optional

from stroke_seg.logging_config import get_logger
from stroke_seg.exceptions import ModelCreationException
from .bash_client import BashClient
from .fs_client import create_temp_file, cleanup_file


class SbatchClient:
    """Handles sbatch-specific operations using the generic BashClient."""
    
    def __init__(self, bash_client: Optional[BashClient] = None):
        """
        Initialize the sbatch client.
        
        Args:
            bash_client: BashClient instance to use (creates new one if None)
        """
        self.logger = get_logger(__name__)
        self.bash_client = bash_client or BashClient()
    
    def extract_job_id(self, sbatch_output: str) -> str:
        """
        Extract job ID from sbatch command output.
        
        Args:
            sbatch_output: Output from sbatch command
            
        Returns:
            Job ID as string
            
        Raises:
            ModelCreationException: If job ID cannot be extracted
        """
        try:
            # Look for pattern "Submitted batch job XXXXXX"
            match = re.search(r'Submitted batch job (\d+)', sbatch_output)
            
            if not match:
                error_msg = f"Could not extract job ID from sbatch output: {sbatch_output}"
                self.logger.error(error_msg)
                raise ModelCreationException(error_msg)
            
            job_id = match.group(1)
            self.logger.debug(f"Extracted job ID: {job_id}")
            return job_id
            
        except Exception as e:
            error_msg = f"Failed to extract job ID: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
    
    def submit_sbatch_job(self, sbatch_content: str) -> str:
        """
        Create sbatch file, submit it, and return job ID with cleanup.
        
        Args:
            sbatch_content: Content for the sbatch file
            
        Returns:
            Batch job ID as string
            
        Raises:
            ModelCreationException: If any step fails
        """
        sbatch_file_path = None
        
        try:
            # Create temporary sbatch file
            sbatch_file_path = create_temp_file(
                content=sbatch_content, 
                suffix='.sbatch'
            )
            
            # Execute sbatch command
            sbatch_output = self.bash_client.execute_command_with_success_check(
                ['sbatch', sbatch_file_path]
            )
            
            # Extract job ID from output
            job_id = self.extract_job_id(sbatch_output)
            
            self.logger.info(f"Sbatch job submitted successfully - Job ID: {job_id}")
            return job_id
            
        finally:
            # Always cleanup temporary file
            if sbatch_file_path:
                cleanup_file(sbatch_file_path)
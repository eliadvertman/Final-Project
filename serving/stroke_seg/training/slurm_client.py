"""Sbatch client for SLURM job submission operations."""

import re
from typing import Optional, Dict, Any
from datetime import datetime

from stroke_seg.logging_config import get_logger
from stroke_seg.exceptions import ModelCreationException
from .bash_client import BashClient
from .fs_client import create_temp_file, cleanup_file
from .slurm_parser import parse_scontrol_output, extract_job_summary


class SlurmClient:
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
    
    def _create_completed_job_summary(self, job_id: str) -> Dict[str, Any]:
        """
        Create a job summary for a job that no longer exists in SLURM.
        
        This handles the case where a job has completed and been removed from
        the SLURM queue, which is normal behavior. We treat this as successful
        completion.
        
        Args:
            job_id: SLURM job ID that was not found
            
        Returns:
            Job summary dictionary indicating successful completion
        """
        current_time = datetime.now()
        
        return {
            'job_id': job_id,
            'state': 'NOT_FOUND',  # Special state indicating job was removed from queue
            'internal_status': 'COMPLETED',  # Assume successful completion
            'start_time': None,  # Unknown - job already removed
            'end_time': current_time,  # Use current time as completion time
            'exit_code': '0:0',  # Assume successful exit
            'reason': 'Job completed and removed from SLURM queue',
            'is_finished': True,
            'is_successful': True,  # Treat missing jobs as successful
            'error_message': None,  # Not an error condition
        }
    
    def get_job_status(self, job_id: str) -> Optional[str]:
        """
        Get SLURM job status using scontrol.
        
        Args:
            job_id: SLURM job ID
            
        Returns:
            Job status string (e.g., 'RUNNING', 'PENDING', 'COMPLETED') or None if not found
            
        Raises:
            ModelCreationException: If scontrol command fails
        """
        try:
            self.logger.debug(f"Getting job status for job ID: {job_id}")
            
            # Execute scontrol show job command
            scontrol_output = self.bash_client.execute_command_with_success_check(
                ['scontrol', 'show', 'job', job_id]
            )
            
            # Parse output to extract job state
            job_info = parse_scontrol_output(scontrol_output)
            job_state = job_info.get('JobState')
            
            self.logger.debug(f"Job {job_id} status: {job_state}")
            return job_state
            
        except Exception as e:
            error_msg = f"Failed to get job status for {job_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
    
    def get_job_info(self, job_id: str) -> Dict[str, Any]:
        """
        Get comprehensive job information using scontrol.
        
        Handles jobs that no longer exist in SLURM (completed and removed)
        by treating them as successfully completed.
        
        Args:
            job_id: SLURM job ID
            
        Returns:
            Dictionary containing parsed job information with summary fields
            
        Raises:
            ModelCreationException: If scontrol command execution fails (not job missing)
        """
        try:
            self.logger.debug(f"Getting job information for job ID: {job_id}")
            
            # Execute scontrol show job command (don't use success_check to handle missing jobs)
            stdout, stderr, return_code = self.bash_client.execute_command(
                ['scontrol', 'show', 'job', job_id]
            )
            
            if return_code == 0:
                # Job exists - parse normally
                self.logger.debug(f"Job {job_id} found in SLURM queue")
                job_info = parse_scontrol_output(stdout)
                job_summary = extract_job_summary(job_info)
                
                self.logger.debug(f"Job {job_id} info retrieved - State: {job_summary.get('state')}")
                return job_summary
                
            else:
                # Job doesn't exist - assume completed and removed from queue
                self.logger.info(f"Job {job_id} not found in SLURM queue - treating as completed")
                self.logger.debug(f"scontrol stderr for missing job {job_id}: {stderr}")
                
                completed_summary = self._create_completed_job_summary(job_id)
                return completed_summary
            
        except Exception as e:
            error_msg = f"Failed to execute scontrol command for job {job_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
    
    def is_job_active(self, job_id: str) -> bool:
        """
        Check if job is in an active state (PENDING or RUNNING).
        
        Args:
            job_id: SLURM job ID
            
        Returns:
            True if job is active, False otherwise
        """
        try:
            job_status = self.get_job_status(job_id)
            return job_status in ['PENDING', 'RUNNING', 'SUSPENDED']
        except Exception as e:
            self.logger.warning(f"Could not check if job {job_id} is active: {str(e)}")
            return False
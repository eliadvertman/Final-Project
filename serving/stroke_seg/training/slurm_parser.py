"""SLURM scontrol output parsing utilities."""

import re
from datetime import datetime
from typing import Dict, Optional, Any
from stroke_seg.logging_config import get_logger

logger = get_logger(__name__)


def parse_scontrol_output(scontrol_output: str) -> Dict[str, Any]:
    """
    Parse scontrol show job output into a structured dictionary.
    
    Args:
        scontrol_output: Raw output from 'scontrol show job [job_id]' command
        
    Returns:
        Dictionary containing parsed job information
        
    Raises:
        ValueError: If output cannot be parsed
    """
    if not scontrol_output or scontrol_output.strip() == "":
        raise ValueError("Empty scontrol output")
    
    job_info = {}
    
    try:
        # Parse each line and extract key=value pairs
        for line in scontrol_output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Remove line numbers if present (format: "   5→   JobState=RUNNING")
            line = re.sub(r'^\s*\d+→\s*', '', line)
            
            # Split line by spaces and extract key=value pairs
            parts = re.findall(r'(\w+)=([^\s]+(?:\s+[^\s=]+)*?)(?=\s+\w+=|$)', line)
            
            for key, value in parts:
                job_info[key] = value.strip()
    
    except Exception as e:
        logger.error(f"Failed to parse scontrol output: {str(e)}")
        raise ValueError(f"Failed to parse scontrol output: {str(e)}")
    
    if not job_info:
        raise ValueError("No job information found in scontrol output")
    
    return job_info


def extract_job_id(job_info: Dict[str, Any]) -> Optional[str]:
    """Extract job ID from parsed job information."""
    return job_info.get('JobId')


def extract_job_state(job_info: Dict[str, Any]) -> Optional[str]:
    """Extract job state from parsed job information."""
    return job_info.get('JobState')


def extract_exit_code(job_info: Dict[str, Any]) -> Optional[str]:
    """Extract exit code from parsed job information."""
    return job_info.get('ExitCode')


def extract_job_reason(job_info: Dict[str, Any]) -> Optional[str]:
    """Extract job failure reason from parsed job information."""
    return job_info.get('Reason')


def is_job_successful(job_info: Dict[str, Any]) -> bool:
    """
    Check if job completed successfully based on exit code.
    
    Args:
        job_info: Parsed job information dictionary
        
    Returns:
        True if job completed successfully (exit code 0:0)
    """
    exit_code = extract_exit_code(job_info)
    return exit_code == '0:0' if exit_code else False


def extract_error_message(job_info: Dict[str, Any]) -> Optional[str]:
    """
    Extract error message from failed job information.
    
    Args:
        job_info: Parsed job information dictionary
        
    Returns:
        Error message string or None if no error found
    """
    job_state = extract_job_state(job_info)
    exit_code = extract_exit_code(job_info)
    reason = extract_job_reason(job_info)
    
    # If job is not in a failed state, no error message
    if not is_job_finished(job_state or '') or is_job_successful(job_info):
        return None
    
    # Build error message from available information
    error_parts = []
    
    if job_state:
        error_parts.append(f"Job state: {job_state}")
    
    if exit_code and exit_code != '0:0':
        error_parts.append(f"Exit code: {exit_code}")
    
    if reason and reason not in ['None', '(null)', 'N/A']:
        error_parts.append(f"Reason: {reason}")
    
    # Add specific error messages based on state
    if job_state == 'CANCELLED':
        error_parts.append("Job was cancelled")
    elif job_state == 'TIMEOUT':
        error_parts.append("Job exceeded time limit")
    elif job_state == 'OUT_OF_MEMORY':
        error_parts.append("Job ran out of memory")
    elif job_state == 'NODE_FAIL':
        error_parts.append("Node failure occurred")
    elif job_state == 'FAILED':
        if exit_code and exit_code != '0:0':
            error_parts.append("Job failed with non-zero exit code")
        else:
            error_parts.append("Job failed")
    
    return "; ".join(error_parts) if error_parts else f"Job failed with state: {job_state}"


def parse_slurm_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse SLURM timestamp format to datetime object.
    
    Args:
        timestamp_str: Timestamp string from SLURM (e.g., "2025-09-13T12:14:02")
        
    Returns:
        datetime object or None if parsing fails
    """
    if not timestamp_str or timestamp_str in ['Unknown', 'N/A', '(null)', 'None']:
        return None
    
    try:
        # Handle SLURM timestamp format: 2025-09-13T12:14:02
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        logger.warning(f"Failed to parse timestamp: {timestamp_str}")
        return None


def extract_start_time(job_info: Dict[str, Any]) -> Optional[datetime]:
    """Extract and parse start time from job information."""
    start_time_str = job_info.get('StartTime')
    return parse_slurm_timestamp(start_time_str) if start_time_str else None


def extract_end_time(job_info: Dict[str, Any]) -> Optional[datetime]:
    """Extract and parse end time from job information."""
    end_time_str = job_info.get('EndTime')
    return parse_slurm_timestamp(end_time_str) if end_time_str else None


def map_slurm_state_to_job_status(slurm_state: str) -> str:
    """
    Map SLURM job states to internal job status values.
    
    Args:
        slurm_state: SLURM job state (e.g., RUNNING, PENDING, COMPLETED, NOT_FOUND)
        
    Returns:
        Internal job status (PENDING, RUNNING, COMPLETED, FAILED)
    """
    state_mapping = {
        'PENDING': 'PENDING',
        'RUNNING': 'RUNNING', 
        'COMPLETED': 'COMPLETED',
        'FAILED': 'FAILED',
        'CANCELLED': 'FAILED',
        'TIMEOUT': 'FAILED',
        'OUT_OF_MEMORY': 'FAILED',
        'NODE_FAIL': 'FAILED',
        'PREEMPTED': 'FAILED',
        'SUSPENDED': 'RUNNING',  # Treat suspended as still running
        'NOT_FOUND': 'COMPLETED',  # Job completed and removed from queue
    }
    
    return state_mapping.get(slurm_state, 'FAILED')


def is_job_finished(slurm_state: str) -> bool:
    """
    Check if job is in a finished state.
    
    Args:
        slurm_state: SLURM job state
        
    Returns:
        True if job is finished (completed or failed)
    """
    finished_states = {'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT', 'OUT_OF_MEMORY', 'NODE_FAIL', 'NOT_FOUND'}
    return slurm_state in finished_states


def extract_job_summary(job_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key job information for status updates.
    
    Args:
        job_info: Parsed job information dictionary
        
    Returns:
        Dictionary with essential job status information
    """
    job_state = extract_job_state(job_info) or ''
    internal_status = map_slurm_state_to_job_status(job_state)
    
    return {
        'job_id': extract_job_id(job_info),
        'state': job_state,
        'internal_status': internal_status,
        'start_time': extract_start_time(job_info),
        'end_time': extract_end_time(job_info),
        'exit_code': extract_exit_code(job_info),
        'reason': extract_job_reason(job_info),
        'is_finished': is_job_finished(job_state),
        'is_successful': is_job_successful(job_info),
        'error_message': extract_error_message(job_info) if internal_status == 'FAILED' else None,
    }


def is_valid_state_transition(current_status: str, new_status: str) -> bool:
    """
    Validate if state transition is allowed according to state machine rules.
    
    Args:
        current_status: Current job status (PENDING, RUNNING, COMPLETED, FAILED)
        new_status: New job status to transition to
        
    Returns:
        True if transition is valid, False otherwise
    """
    # Define valid transitions based on state machine diagram
    valid_transitions = {
        'PENDING': {'RUNNING', 'FAILED'},           # PENDING can go to RUNNING or FAILED
        'RUNNING': {'COMPLETED', 'FAILED'},         # RUNNING can go to COMPLETED or FAILED  
        'COMPLETED': set(),                         # COMPLETED is terminal
        'FAILED': set()                             # FAILED is terminal
    }
    
    # Allow staying in the same state (no transition)
    if current_status == new_status:
        return True
    
    # Check if transition is valid
    allowed_states = valid_transitions.get(current_status, set())
    return new_status in allowed_states


def should_monitor_job_status(job_status: str) -> bool:
    """
    Check if job status should be monitored according to state machine.
    
    Args:
        job_status: Current job status
        
    Returns:
        True if job should be monitored (non-terminal states)
    """
    # Monitor only non-terminal states as per state machine diagram
    return job_status in {'PENDING', 'RUNNING'}


def get_state_transition_reason(current_status: str, new_status: str, job_info: Dict[str, Any]) -> str:
    """
    Get a descriptive reason for the state transition.
    
    Args:
        current_status: Current job status
        new_status: New job status
        job_info: Parsed job information
        
    Returns:
        Human-readable transition reason
    """
    if current_status == new_status:
        return f"Status unchanged: {current_status}"
    
    slurm_state = job_info.get('state', 'Unknown')
    exit_code = job_info.get('exit_code')
    
    if new_status == 'RUNNING':
        return f"Job started running (SLURM state: {slurm_state})"
    elif new_status == 'COMPLETED':
        if slurm_state == 'NOT_FOUND':
            return f"Job completed and removed from SLURM queue (assumed successful)"
        elif exit_code == '0:0':
            return f"Job completed successfully (SLURM state: {slurm_state}, Exit code: {exit_code})"
        else:
            return f"Job completed (SLURM state: {slurm_state}, Exit code: {exit_code})"
    elif new_status == 'FAILED':
        reason = job_info.get('reason', '')
        if reason and reason not in ['None', '(null)', 'N/A']:
            return f"Job failed (SLURM state: {slurm_state}, Reason: {reason})"
        else:
            return f"Job failed (SLURM state: {slurm_state})"
    else:
        return f"Status changed from {current_status} to {new_status} (SLURM state: {slurm_state})"
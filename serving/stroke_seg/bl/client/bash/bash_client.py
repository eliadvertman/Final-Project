"""Generic bash client for executing commands."""

import subprocess
from typing import List, Union, Tuple, Optional

from stroke_seg.exceptions import ModelCreationException
from stroke_seg.logging_config import get_logger


class BashClient:
    """Generic bash command executor."""
    
    def __init__(self, default_timeout: int = 30):
        """
        Initialize the bash client.
        
        Args:
            default_timeout: Default timeout for commands in seconds
        """
        self.logger = get_logger(__name__)
        self.default_timeout = default_timeout

    def execute_command(self, command: Union[str, List[str]], timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Execute a bash command and return output.
        
        Args:
            command: Command to execute (string or list of args)
            timeout: Command timeout in seconds (uses default if None)
            
        Returns:
            Tuple of (stdout, stderr, return_code)
            
        Raises:
            ModelCreationException: If command execution fails
        """
        timeout = timeout or self.default_timeout
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=isinstance(command, str)
            )
            
            self.logger.debug(f"Command executed: {command}, Return code: {result.returncode}")
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds: {command}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        except FileNotFoundError:
            error_msg = f"Command not found: {command}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)

    def execute_command_with_success_check(self, command: Union[str, List[str]], timeout: Optional[int] = None) -> str:
        """
        Execute command and raise exception if it fails.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command stdout
            
        Raises:
            ModelCreationException: If command fails or returns non-zero exit code
        """
        stdout, stderr, return_code = self.execute_command(command, timeout)
        
        if return_code != 0:
            error_msg = f"Command failed with exit code {return_code}: {command}\nStderr: {stderr}"
            self.logger.error(error_msg)
            raise ModelCreationException(error_msg)
        
        return stdout
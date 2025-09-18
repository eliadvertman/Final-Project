import os
import tempfile

from stroke_seg.logging_config import get_logger

logger = get_logger(__name__)

def create_temp_file(content: str, suffix: str = '.tmp') -> str:
    """
    Create a temporary file with specified content.

    Args:
        content: Content to write to the file
        suffix: File suffix/extension

    Returns:
        Path to the created temporary file

    Raises:
        ModelCreationException: If file creation fails
    """
    try:
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, text=True)

        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)

        logger.debug(f"Temporary file created: {temp_path}")
        return temp_path

    except Exception as e:
        error_msg = f"Failed to create temporary file: {str(e)}"
        logger.error(error_msg)
        raise

def cleanup_file(file_path: str) -> None:
    """
    Clean up a temporary file.

    Args:
        file_path: Path to the file to remove
    """
    try:
        os.unlink(file_path)
        logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

def create_dir(directory_path: str) -> None:
    """
    Create a directory and all necessary parent directories.

    Args:
        directory_path: Path to the directory to create

    Raises:
        Exception: If directory creation fails
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        logger.debug(f"Directory created: {directory_path}")
    except Exception as e:
        error_msg = f"Failed to create directory {directory_path}: {str(e)}"
        logger.error(error_msg)
        raise
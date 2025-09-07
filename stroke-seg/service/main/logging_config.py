"""Centralized logging configuration for the ML prediction service."""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional
import uuid
from flask import request, has_request_context


class RequestContextFilter(logging.Filter):
    """Filter to add request context information to log records."""
    
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(request, 'request_id', 'no-request-id')
            record.method = request.method
            record.path = request.path
            record.remote_addr = request.remote_addr
        else:
            record.request_id = 'no-request-id'
            record.method = '-'
            record.path = '-'
            record.remote_addr = '-'
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', 'no-request-id'),
            'method': getattr(record, 'method', '-'),
            'path': getattr(record, 'path', '-'),
            'remote_addr': getattr(record, 'remote_addr', '-')
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra context if available
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'model_id'):
            log_entry['model_id'] = record.model_id
        if hasattr(record, 'predict_id'):
            log_entry['predict_id'] = record.predict_id
            
        return str(log_entry).replace("'", '"')


def setup_logging(app_name: str = 'pic_service', log_level: Optional[str] = None):
    """
    Setup centralized logging configuration.
    
    Args:
        app_name: Name of the application for logging context
        log_level: Log level override (DEBUG, INFO, WARNING, ERROR)
    """
    # Determine log level from environment or parameter
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Determine log format from environment
    log_format = os.getenv('LOG_FORMAT', 'standard')  # standard or json
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create request context filter
    request_filter = RequestContextFilter()
    
    # Setup formatter based on environment
    if log_format.lower() == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(method)s %(path)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_filter)
    root_logger.addHandler(console_handler)
    
    # Setup file logging if enabled
    log_file = os.getenv('LOG_FILE')
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level, logging.INFO))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_filter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Setup application logger
    app_logger = logging.getLogger(app_name)
    app_logger.info(f"Logging configured - Level: {log_level}, Format: {log_format}")
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def add_request_id_to_request():
    """Middleware function to add request ID to Flask request context."""
    if has_request_context():
        request.request_id = str(uuid.uuid4())


def log_request_info(logger: logging.Logger, start_time: float, status_code: int):
    """
    Log request completion information.
    
    Args:
        logger: Logger instance
        start_time: Request start timestamp
        status_code: HTTP status code
    """
    if has_request_context():
        duration = (datetime.now().timestamp() - start_time) * 1000  # Convert to ms
        logger.info(
            f"Request completed - Status: {status_code}",
            extra={
                'duration': round(duration, 2),
                'status_code': status_code
            }
        )


def log_db_operation(logger: logging.Logger, operation: str, table: str, 
                     duration: Optional[float] = None, record_count: Optional[int] = None):
    """
    Log database operation information.
    
    Args:
        logger: Logger instance
        operation: Database operation (CREATE, READ, UPDATE, DELETE, LIST)
        table: Database table name
        duration: Operation duration in milliseconds
        record_count: Number of records affected
    """
    extra = {'operation': operation, 'table': table}
    if duration is not None:
        extra['duration'] = round(duration, 2)
    if record_count is not None:
        extra['record_count'] = record_count
        
    logger.info(f"DB {operation} on {table}", extra=extra)
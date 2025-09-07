"""Custom exceptions for the ML prediction service."""


class ServiceException(Exception):
    """Base exception for all service-related errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ClientException(ServiceException):
    """Base exception for client errors (4xx status codes)."""
    
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)


class ServerException(ServiceException):
    """Base exception for server errors (5xx status codes)."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)


# Client Error Exceptions (4xx)
class InvalidJSONException(ClientException):
    """Exception raised when JSON payload is invalid or malformed."""
    
    def __init__(self, message: str = "Invalid JSON payload"):
        super().__init__(message, 400)


class InvalidUUIDException(ClientException):
    """Exception raised when a UUID format is invalid."""
    
    def __init__(self, field_name: str = "ID"):
        message = f"Invalid {field_name} format"
        super().__init__(message, 400)


class InvalidPaginationException(ClientException):
    """Exception raised when pagination parameters are invalid."""
    
    def __init__(self, parameter: str):
        message = f"{parameter} must be non-negative"
        super().__init__(message, 400)


class MissingRequiredFieldException(ClientException):
    """Exception raised when required fields are missing."""
    
    def __init__(self, field_name: str):
        message = f"Missing required field: {field_name}"
        super().__init__(message, 400)


class ModelNotReadyException(ClientException):
    """Exception raised when a model is not ready for predictions."""
    
    def __init__(self, status: str = None):
        message = f"Model is not ready for predictions (status: {status})" if status else "Model is not ready for predictions"
        super().__init__(message, 400)


class ModelNotFoundException(ClientException):
    """Exception raised when a model is not found."""
    
    def __init__(self, model_id: str = None):
        message = f"Model {model_id} not found" if model_id else "Model not found"
        super().__init__(message, 404)


class PredictionNotFoundException(ClientException):
    """Exception raised when a prediction is not found."""
    
    def __init__(self, predict_id: str = None):
        message = f"Prediction {predict_id} not found" if predict_id else "Prediction not found"
        super().__init__(message, 404)


class InvalidModelStateException(ClientException):
    """Exception raised when model is in invalid state for operation."""
    
    def __init__(self, current_state: str, required_states: list):
        message = f"Model is in '{current_state}' state, but requires one of: {', '.join(required_states)}"
        super().__init__(message, 409)


# Server Error Exceptions (5xx)
class DatabaseException(ServerException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, 500)


class DatabaseConnectionException(ServerException):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, 503)


class ModelCreationException(ServerException):
    """Exception raised when model creation fails due to server error."""
    
    def __init__(self, message: str = "Model creation failed"):
        super().__init__(message, 500)


class PredictionProcessingException(ServerException):
    """Exception raised when prediction processing fails."""
    
    def __init__(self, message: str = "Prediction processing failed"):
        super().__init__(message, 500)
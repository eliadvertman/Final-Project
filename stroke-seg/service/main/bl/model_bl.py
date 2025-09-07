"""Business logic layer for model management operations."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..dao.model_dao import ModelDAO
from ..dao.models import ModelRecord
from ..exceptions import (
    ModelNotFoundException,
    InvalidUUIDException,
    InvalidPaginationException,
    DatabaseException,
    ModelCreationException,
    DatabaseConnectionException,
    MissingRequiredFieldException
)
from ..logging_config import get_logger


class ModelBL:
    """Business logic class for model management operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAO."""
        self.model_dao = ModelDAO()
        self.logger = get_logger(__name__)
    
    def train_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate model training with the provided configuration.
        
        Args:
            data: Training configuration data
            
        Returns:
            Dict containing success message and model ID
            
        Raises:
            ModelCreationException: If model creation fails due to server error
            DatabaseConnectionException: If database connection fails
        """
        model_name = data.get('modelName', 'Unnamed Model')
        self.logger.info(f"Starting model training - Name: {model_name}")
        
        try:
            model_record = ModelRecord(
                name=model_name,
                images_path=data.get('imagesPath'),
                labels_path=data.get('labelsPath'),
                dataset_path=data.get('datasetPath'),
                status='PENDING',
                progress=0.0,
                start_time=datetime.now()
            )
            
            self.model_dao.create(model_record)
            
            self.logger.info(
                f"Model training record created - ID: {model_record.model_id}, Name: {model_name}",
                extra={'model_id': str(model_record.model_id)}
            )
            
            return {
                "message": "Model training started.",
                "modelId": str(model_record.model_id)
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Model training failed - Name: {model_name}, Error: {str(e)}")
            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise ModelCreationException(f"Failed to create model: {str(e)}")
    
    def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific model.
        
        Args:
            model_id: UUID string of the model
            
        Returns:
            Dict containing model status information
            
        Raises:
            InvalidUUIDException: If model ID format is invalid
            ModelNotFoundException: If model is not found
        """
        self.logger.debug(f"Getting model status - ID: {model_id}")
        
        try:
            model_uuid = uuid.UUID(model_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for model ID: {model_id}")
            raise InvalidUUIDException("model ID")
        
        model_record = self.model_dao.get_by_model_id(model_uuid)
        
        if not model_record:
            self.logger.warning(f"Model not found - ID: {model_id}")
            raise ModelNotFoundException(model_id)
        
        self.logger.debug(
            f"Model status retrieved - ID: {model_id}, Status: {model_record.status}, Progress: {model_record.progress}%",
            extra={'model_id': model_id}
        )
        
        response = {
            "modelId": str(model_record.model_id),
            "status": model_record.status,
            "progress": model_record.progress
        }
        
        if model_record.start_time:
            response["startTime"] = model_record.start_time.isoformat() + 'Z'
        if model_record.end_time:
            response["endTime"] = model_record.end_time.isoformat() + 'Z'
        if model_record.error_message:
            response["errorMessage"] = model_record.error_message
            
        return response
    
    def list_models(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all models with pagination.
        
        Args:
            limit: Maximum number of models to return
            offset: Number of models to skip
            
        Returns:
            List of model summary dictionaries
            
        Raises:
            InvalidPaginationException: If pagination parameters are invalid
            DatabaseException: If database operation fails
            DatabaseConnectionException: If database connection fails
        """
        self.logger.debug(f"Listing models - Limit: {limit}, Offset: {offset}")
        
        if limit < 0:
            self.logger.warning(f"Invalid limit parameter: {limit}")
            raise InvalidPaginationException("Limit")
        if offset < 0:
            self.logger.warning(f"Invalid offset parameter: {offset}")
            raise InvalidPaginationException("Offset")
        
        try:
            models = self.model_dao.list_all(limit=limit, offset=offset)
            
            response = []
            for model in models:
                response.append({
                    "modelId": str(model.model_id),
                    "modelName": model.name,
                    "status": model.status,
                    "createdAt": model.created_at.isoformat() + 'Z'
                })
            
            self.logger.info(f"Models listed successfully - Count: {len(response)}, Limit: {limit}, Offset: {offset}")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Failed to list models - Error: {str(e)}")
            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise DatabaseException(f"Failed to list models: {str(e)}")
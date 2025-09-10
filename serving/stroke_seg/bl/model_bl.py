"""Business logic layer for model management operations."""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.models import ModelRecord, TrainingRecord
from stroke_seg.exceptions import (
    ModelNotFoundException,
    InvalidUUIDException,
    InvalidPaginationException,
    DatabaseException,
    ModelCreationException,
    DatabaseConnectionException
)
from stroke_seg.logging_config import get_logger


class ModelBL:
    """Business logic class for model management operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAO."""
        self.model_dao = ModelDAO()
        self.logger = get_logger(__name__)
    
    def create_model(self, training_id: str, model_name: str, model_path: str = None) -> Dict[str, Any]:
        """
        Create a new model record linked to a training.
        
        Args:
            training_id: UUID string of the associated training
            model_name: Name for the model
            model_path: Optional path to the trained model file
            
        Returns:
            Dict containing success message and model ID
            
        Raises:
            InvalidUUIDException: If training ID format is invalid
            ModelCreationException: If model creation fails due to server error
            DatabaseConnectionException: If database connection fails
        """
        self.logger.info(f"Creating model - Name: {model_name}, Training ID: {training_id}")
        
        try:
            training_uuid = uuid.UUID(training_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for training ID: {training_id}")
            raise InvalidUUIDException("training ID")
        
        try:
            # Get the training record to ensure it exists
            training_record = TrainingRecord.get(TrainingRecord.id == str(training_uuid))
            
            # Create model record linked to training
            model_record = ModelRecord(
                training_id=training_record,
                model_name=model_name,
                model_path=model_path,
                created_at=datetime.now()
            )
            
            self.model_dao.create(model_record)
            
            self.logger.info(
                f"Model created - ID: {model_record.id}, Name: {model_record.model_name}, Training ID: {training_id}",
                extra={'model_id': str(model_record.id), 'training_id': training_id}
            )
            
            return {
                "message": "Model created successfully.",
                "modelId": str(model_record.id)
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Model creation failed - Name: {model_name}, Error: {str(e)}")
            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise ModelCreationException(f"Failed to create model: {str(e)}")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: UUID string of the model
            
        Returns:
            Dict containing model information including training status
            
        Raises:
            InvalidUUIDException: If model ID format is invalid
            ModelNotFoundException: If model is not found
        """
        self.logger.debug(f"Getting model info - ID: {model_id}")
        
        try:
            model_uuid = uuid.UUID(model_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for model ID: {model_id}")
            raise InvalidUUIDException("model ID")
        
        # Get the model record
        model_record = self.model_dao.get_by_id(model_uuid)
        
        if not model_record:
            self.logger.warning(f"Model not found - ID: {model_id}")
            raise ModelNotFoundException(model_id)
        
        # Get the associated training record for status
        training_record = model_record.training_id
        
        self.logger.debug(
            f"Model info retrieved - ID: {model_id}, Training Status: {training_record.status}",
            extra={'model_id': model_id}
        )
        
        response = {
            "modelId": str(model_record.id),
            "modelName": model_record.model_name,
            "modelPath": model_record.model_path,
            "trainingId": str(training_record.id),
            "trainingStatus": training_record.status,
            "progress": training_record.progress,
            "createdAt": model_record.created_at.isoformat() + 'Z' if model_record.created_at else None
        }
        
        if training_record.start_time:
            response["trainingStartTime"] = training_record.start_time.isoformat() + 'Z'
        if training_record.end_time:
            response["trainingEndTime"] = training_record.end_time.isoformat() + 'Z'
        if training_record.error_message:
            response["errorMessage"] = training_record.error_message
            
        return response
    
    def list_models(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all trained models with pagination.
        
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
                    "modelId": str(model.id),
                    "modelName": model.model_name,
                    "trainingStatus": model.training_id.status,  # Get status from training record
                    "createdAt": model.created_at.isoformat() + 'Z' if model.created_at else None,
                    "modelPath": model.model_path
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
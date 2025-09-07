"""Business logic layer for inference/prediction operations."""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from stroke_seg.dao.inference_dao import InferenceDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.models import InferenceRecord
from stroke_seg.exceptions import (
    ModelNotFoundException,
    PredictionNotFoundException,
    InvalidUUIDException,
    ModelNotReadyException,
    InvalidPaginationException,
    DatabaseException
)


class InferenceBL:
    """Business logic class for inference/prediction operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAOs."""
        self.inference_dao = InferenceDAO()
        self.model_dao = ModelDAO()
    
    def make_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction using a specified model.
        
        Args:
            data: Prediction request data containing modelId and inputData
            
        Returns:
            Dict containing prediction result and metadata
            
        Raises:
            InvalidUUIDException: If model ID format is invalid
            ModelNotFoundException: If model is not found
            ModelNotReadyException: If model is not ready for predictions
            DatabaseException: If prediction creation fails
        """
        try:
            model_uuid = uuid.UUID(data.get('modelId', ''))
        except (ValueError, TypeError):
            raise InvalidUUIDException("model ID")
        
        model_record = self.model_dao.get_by_model_id(model_uuid)
        
        if not model_record:
            raise ModelNotFoundException(str(model_uuid))
        
        if model_record.status not in ['TRAINED', 'DEPLOYED']:
            raise ModelNotReadyException(model_record.status)
        
        # Mock prediction logic
        prediction_result = {"result": "mock_prediction", "confidence": 0.95}
        
        try:
            inference_record = InferenceRecord(
                model_id=model_record,
                input_data=data.get('inputData', {}),
                prediction=prediction_result,
                status='COMPLETED',
                start_time=datetime.now(),
                end_time=datetime.now()
            )
            
            self.inference_dao.create(inference_record)
            
            return {
                "predictId": str(inference_record.predict_id),
                "prediction": prediction_result,
                "modelId": str(model_record.model_id),
                "timestamp": inference_record.created_at.isoformat() + 'Z'
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to create prediction: {str(e)}")
    
    def get_prediction_status(self, predict_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific prediction.
        
        Args:
            predict_id: UUID string of the prediction
            
        Returns:
            Dict containing prediction status information
            
        Raises:
            InvalidUUIDException: If prediction ID format is invalid
            PredictionNotFoundException: If prediction is not found
        """
        try:
            predict_uuid = uuid.UUID(predict_id)
        except (ValueError, TypeError):
            raise InvalidUUIDException("prediction ID")
        
        inference_record = self.inference_dao.get_by_predict_id(predict_uuid)
        
        if not inference_record:
            raise PredictionNotFoundException(predict_id)
        
        response = {
            "predictId": str(inference_record.predict_id),
            "status": inference_record.status,
            "modelId": str(inference_record.model_id.model_id)
        }
        
        if inference_record.start_time:
            response["startTime"] = inference_record.start_time.isoformat() + 'Z'
        if inference_record.end_time:
            response["endTime"] = inference_record.end_time.isoformat() + 'Z'
        if inference_record.error_message:
            response["errorMessage"] = inference_record.error_message
            
        return response
    
    def list_predictions(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all predictions with pagination.
        
        Args:
            limit: Maximum number of predictions to return
            offset: Number of predictions to skip
            
        Returns:
            List of prediction summary dictionaries
            
        Raises:
            InvalidPaginationException: If pagination parameters are invalid
            DatabaseException: If database operation fails
        """
        if limit < 0:
            raise InvalidPaginationException("Limit")
        if offset < 0:
            raise InvalidPaginationException("Offset")
        
        try:
            predictions = self.inference_dao.list_all(limit=limit, offset=offset)
            
            response = []
            for prediction in predictions:
                response.append({
                    "predictId": str(prediction.predict_id),
                    "modelId": str(prediction.model_id.model_id),
                    "status": prediction.status,
                    "createdAt": prediction.created_at.isoformat() + 'Z'
                })
            
            return response
            
        except Exception as e:
            raise DatabaseException(f"Failed to list predictions: {str(e)}")
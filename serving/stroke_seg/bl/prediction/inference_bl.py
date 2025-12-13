"""Business logic layer for inference/prediction operations."""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from stroke_seg.controller.models import InferenceInput
from stroke_seg.config import inference_template_path
from stroke_seg.dao.inference_dao import InferenceDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.models import InferenceRecord, ModelRecord, JobRecord
from stroke_seg.bl.jobs import JobType
from .prediction_facade import PredictionFacade
from stroke_seg.bl.template.template_variables import PredictionTemplateVariables
from stroke_seg.exceptions import (
    ModelNotFoundException,
    PredictionNotFoundException,
    InvalidUUIDException,
    InvalidPaginationException,
    DatabaseException
)


class InferenceBL:
    """Business logic class for inference/prediction operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAOs."""
        self.inference_dao = InferenceDAO()
        self.model_dao = ModelDAO()
        self.job_dao = JobDAO()
        self.prediction_facade = PredictionFacade(inference_template_path)
    
    def make_prediction(self, inference_input : InferenceInput) -> Dict[str, Any]:
        """
        Make a prediction using a specified model.
        
        Args:
            inference_input: Prediction request data containing modelId and input path
            
        Returns:
            Dict containing prediction result and metadata
            
        Raises:
            InvalidUUIDException: If model ID format is invalid
            ModelNotFoundException: If model is not found
            ModelNotReadyException: If model is not ready for predictions
            DatabaseException: If prediction creation fails
        """
        try:
            model_uuid = uuid.UUID(inference_input.model_id)
        except (ValueError, TypeError):
            raise InvalidUUIDException("model ID")
        
        model_record : ModelRecord = self.model_dao.get_by_id(model_uuid)
        
        if not model_record:
            raise ModelNotFoundException(str(model_uuid))

        try:
            # Generate dynamic output directory path
            inference_id = str(uuid.uuid4())
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = f"{model_record.training_id.model_path}/inference/{inference_id}-{current_time}"

            # Prepare variables for sbatch template
            prediction_variables = PredictionTemplateVariables(
                input_path = inference_input.input_path,
                model_name=model_record.model_name,
                model_path=model_record.training_id.model_path,
                output_path=output_dir,
                fold_index=inference_input.fold_index
            )

            # Submit job to Singularity via sbatch
            sbatch_job_id, sbatch_content = self.prediction_facade.submit_prediction_job(prediction_variables)

            # Create job record first
            job_record = JobRecord(
                sbatch_id=sbatch_job_id,
                fold_index=inference_input.fold_index,
                job_type=JobType.INFERENCE.value,
                status='PENDING',
                sbatch_content=sbatch_content
            )
            job_record = self.job_dao.create(job_record)

            # Create inference record with reference to job
            inference_record = InferenceRecord(
                predict_id=inference_id,
                model_id=model_record,
                input_data=inference_input.input_path,
                output_dir=output_dir,
                prediction=None,
                status='PENDING',
                start_time=datetime.now(),
                job_id=job_record
            )

            self.inference_dao.create(inference_record)

            return {
                "predictId": str(inference_record.predict_id),
                "modelId": str(model_record.id),
                "batchJobId": sbatch_job_id,
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
            "modelId": str(inference_record.model_id.id)
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
                    "modelId": str(prediction.model_id.id),
                    "status": prediction.status,
                    "createdAt": prediction.created_at.isoformat() + 'Z'
                })
            
            return response
            
        except Exception as e:
            raise DatabaseException(f"Failed to list predictions: {str(e)}")
"""Business logic layer for training management operations."""
import time
import traceback
import uuid
from datetime import datetime
from typing import List, Dict, Any

from stroke_seg.bl.training import TrainingTemplateVariables
from stroke_seg.bl.training.training_facade import ModelTrainingFacade
from stroke_seg.config import models_base_path, training_template_path
from stroke_seg.controller.models import TrainingConfig
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.models import TrainingRecord, JobRecord
from stroke_seg.dao.training_dao import TrainingDAO
from stroke_seg.exceptions import (
    ModelNotFoundException,
    InvalidUUIDException,
    InvalidPaginationException,
    DatabaseException,
    ModelCreationException,
    DatabaseConnectionException
)
from stroke_seg.logging_config import get_logger


class TrainingBL:
    """Business logic class for training management operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAO and Singularity interface."""
        self.training_dao = TrainingDAO()
        self.job_dao = JobDAO()
        self.model_training_facade = ModelTrainingFacade(training_template_path)
        self.logger = get_logger(__name__)
    
    def train_model(self, training_conf: TrainingConfig) -> Dict[str, Any]:
        """
        Initiate training process.
        
        Args:
            training_conf: Training configuration data
            
        Returns:
            Dict containing success message, training ID, and batch job ID
            
        Raises:
            ModelCreationException: If training creation fails due to server error
            DatabaseConnectionException: If database connection fails
        """
        self.logger.info(f"Starting training - Name: {training_conf.model_name}")
        model_path = f"{models_base_path}/{training_conf.model_name}/{time.time()}"
        
        try:
            # Prepare variables for sbatch template
            training_variables = TrainingTemplateVariables(
                model_name=training_conf.model_name,
                model_path=model_path,
                fold_index=training_conf.fold_index
            )
            
            # Submit job to Singularity via sbatch
            sbatch_job_id, sbatch_content = self.model_training_facade.submit_training_job(training_variables)

            # Create job record first
            job_record = JobRecord(
                sbatch_id=sbatch_job_id,
                fold_index=training_conf.fold_index,
                job_type='TRAINING',
                status='PENDING',
                sbatch_content=sbatch_content
            )
            job_record = self.job_dao.create(job_record)

            # Create training record with reference to job
            training_record = TrainingRecord(
                name=training_conf.model_name,
                images_path=training_conf.images_path,
                labels_path=training_conf.labels_path,
                model_path=model_path,
                job_id=job_record,
                status='TRAINING',
                progress=0.0,
                start_time=datetime.now()
            )

            self.training_dao.create(training_record)

            self.logger.info(
                f"Training record created - ID: {training_record.id}, Name: {training_record.name}",
                extra={'training_id': str(training_record.id)}
            )

            self.logger.info(
                f"Training job submitted - Training ID: {training_record.id}, Job ID: {sbatch_job_id}",
                extra={'training_id': str(training_record.id), 'job_id': sbatch_job_id}
            )
            
            return {
                "message": "Training started.",
                "trainingId": str(training_record.id),
                "batchJobId": sbatch_job_id
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Training failed - Name: {training_conf.model_name}, Error: {str(e)}")
            self.logger.error(traceback.format_exc())

            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:

                raise ModelCreationException(f"Failed to create training: {str(e)}")
    
    def get_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific training.
        
        Args:
            training_id: UUID string of the training
            
        Returns:
            Dict containing training status information
            
        Raises:
            InvalidUUIDException: If training ID format is invalid
            ModelNotFoundException: If training is not found
        """
        self.logger.debug(f"Getting training status - ID: {training_id}")
        
        try:
            training_uuid = uuid.UUID(training_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for training ID: {training_id}")
            raise InvalidUUIDException("training ID")
        
        training_record = self.training_dao.get_by_id(training_uuid)
        
        if not training_record:
            self.logger.warning(f"Training not found - ID: {training_id}")
            raise ModelNotFoundException(training_id)
        
        self.logger.debug(
            f"Training status retrieved - ID: {training_id}, Status: {training_record.status}, Progress: {training_record.progress}%",
            extra={'training_id': training_id}
        )
        
        response = {
            "trainingId": str(training_record.id),
            "status": training_record.status,
            "progress": training_record.progress
        }
        
        if training_record.start_time:
            response["startTime"] = training_record.start_time.isoformat() + 'Z'
        if training_record.end_time:
            response["endTime"] = training_record.end_time.isoformat() + 'Z'
        if training_record.job_id.error_message:
            response["errorMessage"] = training_record.job_id.error_message
            
        return response
    
    def list_trainings(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all trainings with pagination.
        
        Args:
            limit: Maximum number of trainings to return
            offset: Number of trainings to skip
            
        Returns:
            List of training summary dictionaries
            
        Raises:
            InvalidPaginationException: If pagination parameters are invalid
            DatabaseException: If database operation fails
            DatabaseConnectionException: If database connection fails
        """
        self.logger.debug(f"Listing trainings - Limit: {limit}, Offset: {offset}")
        
        if limit < 0:
            self.logger.warning(f"Invalid limit parameter: {limit}")
            raise InvalidPaginationException("Limit")
        if offset < 0:
            self.logger.warning(f"Invalid offset parameter: {offset}")
            raise InvalidPaginationException("Offset")
        
        try:
            trainings = self.training_dao.list_all(limit=limit, offset=offset)
            
            response = []
            for training in trainings:
                response.append({
                    "trainingId": str(training.id),
                    "trainingName": training.name,
                    "status": training.status,
                    "createdAt": training.start_time.isoformat() + 'Z' if training.start_time else None
                })
            
            self.logger.info(f"Trainings listed successfully - Count: {len(response)}, Limit: {limit}, Offset: {offset}")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Failed to list trainings - Error: {str(e)}")
            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise DatabaseException(f"Failed to list trainings: {str(e)}")
    
    def update_training_status(self, training_id: str, status: str, progress: float = None, 
                              error_message: str = None) -> Dict[str, Any]:
        """
        Update the status of a training.
        
        Args:
            training_id: UUID string of the training
            status: New status ('TRAINING', 'TRAINED', 'FAILED')
            progress: Training progress (0.0-100.0)
            error_message: Error message if training failed
            
        Returns:
            Dict containing success message
            
        Raises:
            InvalidUUIDException: If training ID format is invalid
            ModelNotFoundException: If training is not found
        """
        self.logger.debug(f"Updating training status - ID: {training_id}, Status: {status}")
        
        try:
            training_uuid = uuid.UUID(training_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for training ID: {training_id}")
            raise InvalidUUIDException("training ID")
        
        update_data = {"status": status}
        if progress is not None:
            update_data["progress"] = progress
        if error_message is not None:
            update_data["error_message"] = error_message
        if status in ['TRAINED', 'FAILED']:
            update_data["end_time"] = datetime.now()
        
        training_record = self.training_dao.update(training_uuid, **update_data)
        
        if not training_record:
            self.logger.warning(f"Training not found for update - ID: {training_id}")
            raise ModelNotFoundException(training_id)
        
        self.logger.info(
            f"Training status updated - ID: {training_id}, Status: {status}",
            extra={'training_id': training_id}
        )
        
        return {
            "message": "Training status updated successfully.",
            "trainingId": str(training_record.id),
            "status": training_record.status
        }
"""Business logic layer for evaluation management operations."""
import time
import traceback
import uuid
from datetime import datetime
from typing import List, Dict, Any

from stroke_seg.bl.template.template_variables import EvaluationTemplateVariables
from stroke_seg.bl.evaluation.evaluation_facade import EvaluationFacade
from stroke_seg.config import models_base_path, evaluation_template_path
from stroke_seg.controller.models import EvaluationConfig
from stroke_seg.dao.job_dao import JobDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.models import EvaluationRecord, JobRecord
from stroke_seg.dao.evaluation_dao import EvaluationDAO
from stroke_seg.exceptions import (
    ModelNotFoundException,
    InvalidUUIDException,
    InvalidPaginationException,
    DatabaseException,
    ModelCreationException,
    DatabaseConnectionException
)
from stroke_seg.logging_config import get_logger


class EvaluationBL:
    """Business logic class for evaluation management operations."""
    
    def __init__(self):
        """Initialize the business logic layer with DAOs and facade."""
        self.evaluation_dao = EvaluationDAO()
        self.model_dao = ModelDAO()
        self.job_dao = JobDAO()
        self.evaluation_facade = EvaluationFacade(evaluation_template_path)
        self.logger = get_logger(__name__)
    
    def run_evaluation(self, evaluation_conf: EvaluationConfig) -> Dict[str, Any]:
        """
        Initiate evaluation process.
        
        Args:
            evaluation_conf: Evaluation configuration data
            
        Returns:
            Dict containing success message, evaluation ID, and batch job ID
            
        Raises:
            ModelNotFoundException: If model is not found
            ModelCreationException: If evaluation creation fails due to server error
            DatabaseConnectionException: If database connection fails
        """
        self.logger.info(f"Starting evaluation - Model: {evaluation_conf.model_name}, Configurations: {evaluation_conf.configurations}")
        
        try:
            # Find the model by name
            model_record = self.model_dao.get_by_name(evaluation_conf.model_name)
            if not model_record:
                self.logger.warning(f"Model not found - Name: {evaluation_conf.model_name}")
                raise ModelNotFoundException(evaluation_conf.model_name)
            
            # Get model path from training record
            training_record = model_record.training_id
            model_path = training_record.model_path
            
            # Create output path for evaluation results
            output_path = f"{models_base_path}/{evaluation_conf.model_name}/evaluation/{time.time()}"
            
            # Prepare variables for sbatch template
            evaluation_variables = EvaluationTemplateVariables(
                model_name=evaluation_conf.model_name,
                model_path=model_path,
                evaluation_path=evaluation_conf.evaluation_path,
                configurations=list(evaluation_conf.configurations),
                output_path=output_path
            )
            
            # Submit job to Singularity via sbatch
            sbatch_job_id, sbatch_content = self.evaluation_facade.submit_evaluation_job(evaluation_variables)

            # Create job record first
            job_record = JobRecord(
                sbatch_id=sbatch_job_id,
                job_type='EVALUATION',
                status='PENDING',
                sbatch_content=sbatch_content
            )
            job_record = self.job_dao.create(job_record)

            # Create evaluation record with reference to job
            evaluation_record = EvaluationRecord(
                model_id=model_record,
                job_id=job_record,
                evaluation_path=evaluation_conf.evaluation_path,
                configurations=list(evaluation_conf.configurations),
                status='PENDING',
                start_time=datetime.now()
            )

            self.evaluation_dao.create(evaluation_record)

            self.logger.info(
                f"Evaluation record created - ID: {evaluation_record.id}, Model: {evaluation_conf.model_name}",
                extra={'evaluation_id': str(evaluation_record.id)}
            )

            self.logger.info(
                f"Evaluation job submitted - Evaluation ID: {evaluation_record.id}, Job ID: {sbatch_job_id}",
                extra={'evaluation_id': str(evaluation_record.id), 'job_id': sbatch_job_id}
            )
            
            return {
                "message": "Evaluation started.",
                "evaluationId": str(evaluation_record.id),
                "batchJobId": sbatch_job_id
            }
            
        except ModelNotFoundException:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Evaluation failed - Model: {evaluation_conf.model_name}, Error: {str(e)}")
            self.logger.error(traceback.format_exc())

            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise ModelCreationException(f"Failed to create evaluation: {str(e)}")
    
    def get_evaluation_status(self, evaluation_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific evaluation.
        
        Args:
            evaluation_id: UUID string of the evaluation
            
        Returns:
            Dict containing evaluation status information
            
        Raises:
            InvalidUUIDException: If evaluation ID format is invalid
            ModelNotFoundException: If evaluation is not found
        """
        self.logger.debug(f"Getting evaluation status - ID: {evaluation_id}")
        
        try:
            evaluation_uuid = uuid.UUID(evaluation_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for evaluation ID: {evaluation_id}")
            raise InvalidUUIDException("evaluation ID")
        
        evaluation_record = self.evaluation_dao.get_by_id(evaluation_uuid)
        
        if not evaluation_record:
            self.logger.warning(f"Evaluation not found - ID: {evaluation_id}")
            raise ModelNotFoundException(evaluation_id)
        
        self.logger.debug(
            f"Evaluation status retrieved - ID: {evaluation_id}, Status: {evaluation_record.status}",
            extra={'evaluation_id': evaluation_id}
        )
        
        response = {
            "evaluationId": str(evaluation_record.id),
            "modelId": str(evaluation_record.model_id.id),
            "modelName": evaluation_record.model_id.model_name,
            "status": evaluation_record.status,
            "configurations": evaluation_record.configurations,
            "evaluationPath": evaluation_record.evaluation_path
        }
        
        if evaluation_record.start_time:
            response["startTime"] = evaluation_record.start_time.isoformat() + 'Z'
        if evaluation_record.end_time:
            response["endTime"] = evaluation_record.end_time.isoformat() + 'Z'
        if evaluation_record.error_message:
            response["errorMessage"] = evaluation_record.error_message
        if evaluation_record.results:
            response["results"] = evaluation_record.results
            
        return response
    
    def list_evaluations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all evaluations with pagination.
        
        Args:
            limit: Maximum number of evaluations to return
            offset: Number of evaluations to skip
            
        Returns:
            List of evaluation summary dictionaries
            
        Raises:
            InvalidPaginationException: If pagination parameters are invalid
            DatabaseException: If database operation fails
            DatabaseConnectionException: If database connection fails
        """
        self.logger.debug(f"Listing evaluations - Limit: {limit}, Offset: {offset}")
        
        if limit < 0:
            self.logger.warning(f"Invalid limit parameter: {limit}")
            raise InvalidPaginationException("Limit")
        if offset < 0:
            self.logger.warning(f"Invalid offset parameter: {offset}")
            raise InvalidPaginationException("Offset")
        
        try:
            evaluations = self.evaluation_dao.list_all(limit=limit, offset=offset)
            
            response = []
            for evaluation in evaluations:
                response.append({
                    "evaluationId": str(evaluation.id),
                    "modelName": evaluation.model_id.model_name,
                    "evaluationPath": evaluation.evaluation_path,
                    "status": evaluation.status,
                    "configurations": evaluation.configurations,
                    "createdAt": evaluation.created_at.isoformat() + 'Z' if evaluation.created_at else None
                })
            
            self.logger.info(f"Evaluations listed successfully - Count: {len(response)}, Limit: {limit}, Offset: {offset}")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Failed to list evaluations - Error: {str(e)}")
            if "connection" in error_msg or "connect" in error_msg:
                raise DatabaseConnectionException(f"Database connection failed: {str(e)}")
            else:
                raise DatabaseException(f"Failed to list evaluations: {str(e)}")
    
    def update_evaluation_status(self, evaluation_id: str, status: str, 
                                  error_message: str = None, results: Dict = None) -> Dict[str, Any]:
        """
        Update the status of an evaluation.
        
        Args:
            evaluation_id: UUID string of the evaluation
            status: New status ('PENDING', 'EVALUATING', 'COMPLETED', 'FAILED')
            error_message: Error message if evaluation failed
            results: Evaluation results/metrics if completed
            
        Returns:
            Dict containing success message
            
        Raises:
            InvalidUUIDException: If evaluation ID format is invalid
            ModelNotFoundException: If evaluation is not found
        """
        self.logger.debug(f"Updating evaluation status - ID: {evaluation_id}, Status: {status}")
        
        try:
            evaluation_uuid = uuid.UUID(evaluation_id)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid UUID format for evaluation ID: {evaluation_id}")
            raise InvalidUUIDException("evaluation ID")
        
        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message
        if results is not None:
            update_data["results"] = results
        if status in ['COMPLETED', 'FAILED']:
            update_data["end_time"] = datetime.now()
        
        evaluation_record = self.evaluation_dao.update(evaluation_uuid, **update_data)
        
        if not evaluation_record:
            self.logger.warning(f"Evaluation not found for update - ID: {evaluation_id}")
            raise ModelNotFoundException(evaluation_id)
        
        self.logger.info(
            f"Evaluation status updated - ID: {evaluation_id}, Status: {status}",
            extra={'evaluation_id': evaluation_id}
        )
        
        return {
            "message": "Evaluation status updated successfully.",
            "evaluationId": str(evaluation_record.id),
            "status": evaluation_record.status
        }

"""Model management controller for handling model-related HTTP requests."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from stroke_seg.bl.training.training_bl import TrainingBL
from stroke_seg.controller.models import TrainingConfig
from stroke_seg.error_handler import handle_errors
from stroke_seg.logging_config import get_logger


training_bp = Blueprint('training', __name__, url_prefix='/api/v1/training')
training_bl = TrainingBL()
logger = get_logger(__name__)


@training_bp.route('/train', methods=['POST'])
@handle_errors
def train_model():
    """Initiate model training."""
    try:
        raw_data = request.get_json(force=True)
        training_config : TrainingConfig = TrainingConfig.model_validate(raw_data)
        logger.info(f"Model training requested - Name: {training_config.model_name}")
        result = training_bl.train_model(training_config)
        logger.info(f"Model training initiated - ID: {result.get('trainingId')}")
        return jsonify(result), 202

    except ValidationError as e:
        logger.warning(f"Validation error in train_model: {e}")
        raise e(f"Invalid training configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in train_model: {e}")
        raise e


@training_bp.route('/<model_id>/status', methods=['GET'])
@handle_errors
def get_training_status(model_id):
    """Get model training status."""
    logger.info(f"Training status requested - ID: {model_id}")
    result = training_bl.get_training_status(model_id)
    logger.info(f"Training status retrieved - ID: {model_id}, Status: {result.get('status')}")
    return jsonify(result), 200


@training_bp.route('/list', methods=['GET'])
@handle_errors
def list_trainings():
    """List all models with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    logger.debug(f"Trainings list requested - Limit: {limit}, Offset: {offset}")
    result = training_bl.list_trainings(limit=limit, offset=offset)
    logger.info(f"Trainings list retrieved - Count: {len(result) if result else 0}")
    return jsonify(result), 200
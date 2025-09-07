"""Model management controller for handling model-related HTTP requests."""

from flask import Blueprint, request, jsonify

from ..bl.model_bl import ModelBL
from ..error_handler import handle_errors
from ..logging_config import get_logger


model_bp = Blueprint('model', __name__, url_prefix='/api/v1/model')
model_bl = ModelBL()
logger = get_logger(__name__)


@model_bp.route('/train', methods=['POST'])
@handle_errors
def train_model():
    """Initiate model training."""
    data = request.get_json(force=True)
    logger.info(f"Model training requested - Name: {data.get('modelName', 'Unnamed')}")
    result = model_bl.train_model(data)
    logger.info(f"Model training initiated - ID: {result.get('modelId')}")
    return jsonify(result), 202


@model_bp.route('/<model_id>/status', methods=['GET'])
@handle_errors
def get_model_status(model_id):
    """Get model training status."""
    logger.debug(f"Model status requested - ID: {model_id}")
    result = model_bl.get_model_status(model_id)
    logger.debug(f"Model status retrieved - ID: {model_id}, Status: {result.get('status')}")
    return jsonify(result), 200


@model_bp.route('/list', methods=['GET'])
@handle_errors
def list_models():
    """List all models with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    logger.debug(f"Models list requested - Limit: {limit}, Offset: {offset}")
    result = model_bl.list_models(limit=limit, offset=offset)
    logger.info(f"Models list retrieved - Count: {len(result) if result else 0}")
    return jsonify(result), 200
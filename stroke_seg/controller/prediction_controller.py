"""Prediction controller for handling prediction-related HTTP requests."""

from flask import Blueprint, request, jsonify

from stroke_seg.bl.inference_bl import InferenceBL
from stroke_seg.error_handler import handle_errors
from stroke_seg.logging_config import get_logger


prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/v1/predict')
inference_bl = InferenceBL()
logger = get_logger(__name__)


@prediction_bp.route('/predict', methods=['POST'])
@handle_errors
def make_prediction():
    """Make a prediction using a specified model."""
    data = request.get_json(force=True)
    model_id = data.get('modelId', 'unknown')
    logger.info(f"Prediction requested - Model ID: {model_id}")
    result = inference_bl.make_prediction(data)
    logger.info(f"Prediction completed - ID: {result.get('predictId')}, Model: {model_id}")
    return jsonify(result), 200


@prediction_bp.route('/<predict_id>/status', methods=['GET'])
@handle_errors
def get_prediction_status(predict_id):
    """Get prediction status."""
    logger.debug(f"Prediction status requested - ID: {predict_id}")
    result = inference_bl.get_prediction_status(predict_id)
    logger.debug(f"Prediction status retrieved - ID: {predict_id}, Status: {result.get('status')}")
    return jsonify(result), 200


@prediction_bp.route('/list', methods=['GET'])
@handle_errors
def list_predictions():
    """List all predictions with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    logger.debug(f"Predictions list requested - Limit: {limit}, Offset: {offset}")
    result = inference_bl.list_predictions(limit=limit, offset=offset)
    logger.info(f"Predictions list retrieved - Count: {len(result) if result else 0}")
    return jsonify(result), 200
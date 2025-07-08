"""Prediction controller for handling prediction-related HTTP requests."""

from flask import Blueprint, request, jsonify

from ..bl.inference_bl import InferenceBL
from ..error_handler import handle_errors


prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/v1/predict')
inference_bl = InferenceBL()


@prediction_bp.route('/predict', methods=['POST'])
@handle_errors
def make_prediction():
    """Make a prediction using a specified model."""
    data = request.get_json(force=True)
    result = inference_bl.make_prediction(data)
    return jsonify(result), 200


@prediction_bp.route('/<predict_id>/status', methods=['GET'])
@handle_errors
def get_prediction_status(predict_id):
    """Get prediction status."""
    result = inference_bl.get_prediction_status(predict_id)
    return jsonify(result), 200


@prediction_bp.route('/list', methods=['GET'])
@handle_errors
def list_predictions():
    """List all predictions with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = inference_bl.list_predictions(limit=limit, offset=offset)
    return jsonify(result), 200
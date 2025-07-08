"""Model management controller for handling model-related HTTP requests."""

from flask import Blueprint, request, jsonify

from ..bl.model_bl import ModelBL
from ..error_handler import handle_errors


model_bp = Blueprint('model', __name__, url_prefix='/api/v1/model')
model_bl = ModelBL()


@model_bp.route('/train', methods=['POST'])
@handle_errors
def train_model():
    """Initiate model training."""
    data = request.get_json(force=True)
    result = model_bl.train_model(data)
    return jsonify(result), 202


@model_bp.route('/<model_id>/status', methods=['GET'])
@handle_errors
def get_model_status(model_id):
    """Get model training status."""
    result = model_bl.get_model_status(model_id)
    return jsonify(result), 200


@model_bp.route('/list', methods=['GET'])
@handle_errors
def list_models():
    """List all models with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = model_bl.list_models(limit=limit, offset=offset)
    return jsonify(result), 200
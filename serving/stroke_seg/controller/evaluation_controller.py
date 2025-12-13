"""Evaluation controller for handling model evaluation HTTP requests."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from stroke_seg.bl.evaluation.evaluation_bl import EvaluationBL
from stroke_seg.controller.models import EvaluationConfig
from stroke_seg.error_handler import handle_errors
from stroke_seg.logging_config import get_logger


evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/v1/evaluation')
evaluation_bl = EvaluationBL()
logger = get_logger(__name__)


@evaluation_bp.route('/evaluate', methods=['POST'])
@handle_errors
def run_evaluation():
    """Initiate model evaluation."""
    try:
        raw_data = request.get_json(force=True)
        evaluation_config: EvaluationConfig = EvaluationConfig.model_validate(raw_data)
        logger.info(f"Model evaluation requested - Model: {evaluation_config.model_name}, Configurations: {evaluation_config.configurations}")
        result = evaluation_bl.run_evaluation(evaluation_config)
        logger.info(f"Model evaluation initiated - ID: {result.get('evaluationId')}")
        return jsonify(result), 202

    except ValidationError as e:
        logger.warning(f"Validation error in run_evaluation: {e}")
        raise ValueError(f"Invalid evaluation configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in run_evaluation: {e}")
        raise e


@evaluation_bp.route('/<evaluation_id>/status', methods=['GET'])
@handle_errors
def get_evaluation_status(evaluation_id):
    """Get model evaluation status."""
    logger.info(f"Evaluation status requested - ID: {evaluation_id}")
    result = evaluation_bl.get_evaluation_status(evaluation_id)
    logger.info(f"Evaluation status retrieved - ID: {evaluation_id}, Status: {result.get('status')}")
    return jsonify(result), 200


@evaluation_bp.route('/list', methods=['GET'])
@handle_errors
def list_evaluations():
    """List all evaluations with pagination."""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    logger.debug(f"Evaluations list requested - Limit: {limit}, Offset: {offset}")
    result = evaluation_bl.list_evaluations(limit=limit, offset=offset)
    logger.info(f"Evaluations list retrieved - Count: {len(result) if result else 0}")
    return jsonify(result), 200

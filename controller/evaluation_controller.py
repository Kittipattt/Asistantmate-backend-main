from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.evaluation_service import EvaluationService

evaluation_bp = Blueprint('evaluation_controller', __name__)
evaluation_service = EvaluationService()

@evaluation_bp.route('/api/evaluate_ta', methods=['POST'])
def evaluate_ta():
    data = request.json
    response = evaluation_service.evaluate_ta(data)
    return jsonify(response), response.get('status', 200)

@evaluation_bp.route('/api/evaluate', methods=['POST'])
@jwt_required()
def submit_evaluation():
    data = request.get_json()
    identity = get_jwt_identity()
    response = evaluation_service.submit_evaluation(data, identity['Teacher_name'])
    return jsonify(response), response.get('status', 201)

@evaluation_bp.route('/api/evaluate_results', methods=['POST'])
def evaluate_results():
    data = request.get_json()
    response = evaluation_service.get_evaluation_results(data['ta_name'])
    return jsonify(response), response.get('status', 200)

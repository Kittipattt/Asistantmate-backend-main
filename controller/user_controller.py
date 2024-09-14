from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.user_service import UserService

user_bp = Blueprint('user_controller', __name__)
user_service = UserService()

@user_bp.route('/api/current_user', methods=['GET'])
@jwt_required()
def get_current_user():
    identity = get_jwt_identity()
    response = user_service.get_current_user(identity['username'])
    return jsonify(response), response.get('status', 200)

@user_bp.route('/api/current_teacher', methods=['GET'])
@jwt_required()
def get_current_teacher():
    identity = get_jwt_identity()
    response = user_service.get_current_teacher(identity['Teacher_name'])
    return jsonify(response), response.get('status', 200)

@user_bp.route('/api/get_tas', methods=['GET'])
@jwt_required()
def get_tas():
    response = user_service.get_tas()
    return jsonify(response), response.get('status', 200)

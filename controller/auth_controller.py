from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from service.auth_service import AuthService  # Ensure this path is correct

auth_bp = Blueprint('auth_controller', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = auth_service.login(data)
    return jsonify(response), response.get('status', 200)

@auth_bp.route('/login_teacher', methods=['POST'])
def login_teacher():
    data = request.get_json()
    response = auth_service.login_teacher(data)
    return jsonify(response), response.get('status', 200)

@auth_bp.route('/api/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    response = auth_service.student_login(data)
    return jsonify(response), response.get('status', 200)

@auth_bp.route('/api/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    response = auth_service.admin_login(data)
    return jsonify(response), response.get('status', 200)

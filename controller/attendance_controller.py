from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.attendance_service import AttendanceService

attendance_bp = Blueprint('attendance_controller', __name__)
attendance_service = AttendanceService()

@attendance_bp.route('/api/checkin', methods=['POST'])
@jwt_required()
def check_in():
    user_identity = get_jwt_identity()
    data = request.get_json()
    response = attendance_service.check_in(user_identity['username'], data)
    return jsonify(response), response.get('status', 200)

@attendance_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    response = attendance_service.get_attendance()
    return jsonify(response), response.get('status', 200)

@attendance_bp.route('/api/viewattendance', methods=['GET'])
@jwt_required()
def view_attendance():
    user_identity = get_jwt_identity()
    response = attendance_service.view_attendance(user_identity['username'])
    return jsonify(response), response.get('status', 200)

@attendance_bp.route('/api/attendance_summary', methods=['GET'])
@jwt_required()
def get_attendance_summary():
    user_identity = get_jwt_identity()
    response = attendance_service.get_attendance_summary(user_identity['username'])
    return jsonify(response), response.get('status', 200)

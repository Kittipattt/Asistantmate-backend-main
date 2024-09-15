from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.notification_service import NotificationService

notification_bp = Blueprint('notification_controller', __name__)
notification_service = NotificationService()

@notification_bp.route('/api/get_ta_status', methods=['GET'])
@jwt_required()
def get_ta_status():
    username = get_jwt_identity()['username']
    response = notification_service.get_ta_status(username)
    return jsonify(response), response.get('status', 200)

@notification_bp.route('/api/ta_notifications', methods=['GET'])
@jwt_required()
def get_ta_notifications():
    username = get_jwt_identity()['username']
    response = notification_service.get_ta_notifications(username)
    return jsonify(response), response.get('status', 200)

@notification_bp.route('/api/teacher_notifications', methods=['GET'])
@jwt_required()
def get_teacher_notifications():
    teacher_name = get_jwt_identity().get("Teacher_name")
    response = notification_service.get_teacher_notifications(teacher_name)
    return jsonify(response), response.get('status', 200)

@notification_bp.route('/api/approve_notification', methods=['POST'])
@jwt_required()
def approve_notification():
    data = request.get_json()
    teacher_name = get_jwt_identity().get("Teacher_name")
    response = notification_service.approve_notification(data['id'], teacher_name)
    return jsonify(response), response.get('status', 200)

@notification_bp.route('/api/reject_notification', methods=['POST'])
@jwt_required()
def reject_notification():
    data = request.get_json()
    response = notification_service.reject_notification(data['id'])
    return jsonify(response), response.get('status', 200)

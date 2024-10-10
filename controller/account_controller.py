from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.account_service import AccountService

account_bp = Blueprint('account_controller', __name__)
account_service = AccountService()

@account_bp.route('/api/change_username', methods=['POST'])
@jwt_required()
def change_username():
    data = request.get_json()
    current_user = get_jwt_identity()
    username = current_user.get('username')

    new_username = data.get('new_username')

    if not new_username:
        return jsonify({"message": "New username is required"}), 400

    response = account_service.change_username(username, new_username)

    if response.get('status') == 200:
        session['user'] = new_username  # Update session identity
        return jsonify(response), 200
    else:
        return jsonify(response), response.get('status', 500)


@account_bp.route('/api/change_password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    current_user = get_jwt_identity()
    username = current_user.get('username')

    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password:
        return jsonify({"message": "Both new password and confirmation are required"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "New password and confirmation do not match"}), 400

    response = account_service.change_password(username, new_password)

    return jsonify(response), response.get('status', 500)

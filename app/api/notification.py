from flask import Blueprint, jsonify, request
from app.models.notification import Notification, db

notification_api = Blueprint('notification_api', __name__)


@notification_api.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Endpoint to get notifications for a specific user.
    Expects 'user_id' as a query parameter.
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    try:
        # Query the database for notifications belonging to the user
        notifications = Notification.query.filter_by(user_id=user_id).all()
        # Convert each notification to a dictionary and return them
        return jsonify([notif.to_dict() for notif in notifications]), 200
    except Exception as e:
        # Log the exception and return an error message
        print(f"Error when fetching notifications: {e}")
        return jsonify({"error": "Failed to load notifications, please try again later"}), 500

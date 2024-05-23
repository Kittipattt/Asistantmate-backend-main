# api/cancellation.py

from flask import Blueprint, request, jsonify, render_template
from app.models.course import Course
from app.models.cancelled_class import CancelledClass, db
from sqlalchemy import and_
from datetime import datetime

cancellation_api = Blueprint('cancellation_api', __name__)


@cancellation_api.route('/courses', methods=['GET'])
def get_courses():
    try:
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({"error": "Missing teacher ID"}), 400

        courses = Course.query.filter_by(teacher_id=teacher_id).all()
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        print(f"Failed to load courses: {e}")
        return jsonify({"error": "Failed to load courses, please try again later"}), 500


@cancellation_api.route('/cancel_class', methods=['POST'])
def cancel_class():
    data = request.json
    course_id = data.get('course_id')
    cancellation_date = data.get('cancellation_date')

    if not course_id or not cancellation_date:
        return jsonify({"error": "Missing course ID or cancellation date"}), 400

    # Verify the date format
    try:
        cancellation_date = datetime.strptime(cancellation_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format, please use YYYY-MM-DD"}), 400

    # Check for past date
    if cancellation_date < datetime.now():
        return jsonify({"error": "Cannot cancel classes in the past"}), 400

    try:
        # Record the cancellation
        new_cancellation = CancelledClass(
            course_id=course_id,
            cancellation_date=cancellation_date
        )
        db.session.add(new_cancellation)
        db.session.commit()
        return jsonify({"success": "Class cancelled successfully", "cancellation": new_cancellation.to_dict()}), 201
    except Exception as e:
        print(f"Failed to cancel class: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to cancel class, please try again later"}), 500


@cancellation_api.route('/view_cancellations', methods=['GET'])
def view_cancellations():
    try:
        cancellations = CancelledClass.query.all()
        return jsonify([cancellation.to_dict() for cancellation in cancellations]), 200
    except Exception as e:
        print(f"Failed to load cancellations: {e}")
        return jsonify({"error": "Failed to load cancellations, please try again later"}), 500

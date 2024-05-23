# api/attendance.py

from flask import Blueprint, request, jsonify
from app.models.attendance import Attendance, db
from sqlalchemy import and_
from datetime import datetime

attendance_api = Blueprint('attendance_api', __name__)


def check_attendance(course_id, date_time):
    """
    Check if an attendance record exists for the given course_id and date_time.
    """
    try:
        attendance = Attendance.query.filter(
            and_(
                Attendance.course_id == course_id,
                Attendance.date_time == datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
            )
        ).first()
        return attendance is not None
    except Exception as e:
        print(f"Error checking attendance: {e}")
        return False


def record_attendance(course_id, date_time, user_id):
    """
    Record a new attendance entry for the given course_id and date_time.
    """
    try:
        if check_attendance(course_id, date_time):
            print("Attendance already recorded for this course at the specified time.")
            return False  # Return False to indicate that the record already exists

        # Create a new attendance record
        new_attendance = Attendance(
            course_id=course_id,
            date_time=datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S'),
            user_id=user_id
        )
        db.session.add(new_attendance)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error recording attendance: {e}")
        db.session.rollback()
        return False


def get_attendance_history(course_id):
    """
    Retrieve all attendance records for the given course_id.
    """
    try:
        attendance_records = Attendance.query.filter_by(course_id=course_id).all()
        return [record.to_dict() for record in attendance_records]
    except Exception as e:
        print(f"Error getting attendance history: {e}")
        return []


@attendance_api.route('/check', methods=['POST'])
def api_check_attendance():
    """
    API endpoint to check if an attendance record exists.
    """
    data = request.json
    if 'course_id' not in data or 'date_time' not in data:
        return jsonify({"error": "Missing course_id or date_time in the request"}), 400

    exists = check_attendance(data['course_id'], data['date_time'])
    return jsonify({"exists": exists})


@attendance_api.route('/record', methods=['POST'])
def api_record_attendance():
    """
    API endpoint to record a new attendance.
    """
    data = request.json
    if not all(key in data for key in ['course_id', 'date_time', 'user_id']):
        return jsonify({"error": "Missing course_id, date_time, or user_id in the request"}), 400

    success = record_attendance(data['course_id'], data['date_time'], data['user_id'])
    if success:
        return jsonify({"success": "Attendance recorded successfully"}), 201
    else:
        return jsonify({"error": "Failed to record attendance"}), 500


@attendance_api.route('/history', methods=['GET'])
def api_get_attendance_history():
    """
    API endpoint to get attendance history for a course.
    """
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({"error": "Missing course_id in the request"}), 400

    history = get_attendance_history(course_id)
    return jsonify(history)

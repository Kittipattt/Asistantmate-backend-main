from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

from myflaskapp.models.database import db, Attendance, Course, Enrollment
from myflaskapp.models import User

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:201245@localhost:3306/assistant_mate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Ensure the database exists
with app.app_context():
    if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
        create_database(app.config["SQLALCHEMY_DATABASE_URI"])
    db.create_all()

# Set up the login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home route
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the TA Management System!"


# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content


@app.route('/courses', methods=['GET'])
@login_required
def get_courses():
    courses = Course.query.all()
    return jsonify([course.name for course in courses])


@app.route('/enroll', methods=['POST'])
@login_required
def enroll_course():
    course_id = request.json.get('course_id')
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({'message': 'Enrolled successfully'}), 200


# Edit profile
@app.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    user = current_user

    phone_number = request.json.get('phone_number')
    office_room = request.json.get('office_room')

    if phone_number:
        user.phone_number = phone_number

    if office_room:
        user.office_room = office_room

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'office_room': user.office_room
        }
    }), 200


# Check-in
@app.route('/check-in', methods=['POST'])
def check_in():
    user_id = request.json.get('user_id')
    course_id = request.json.get('course_id')

    if not user_id or not course_id:
        return jsonify({'error': 'Missing user_id or course_id'}), 400

    user = User.query.get(user_id)
    if not user or user.role != 'TA':
        return jsonify({'error': 'User not found or not a TA'}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    day_now = datetime.now().strftime("%a")
    if day_now not in course.days:
        return jsonify({'error': 'Check-in not allowed on this day'}), 403

    current_time = int(datetime.now().strftime("%H%M"))
    start_time, end_time = map(int, course.time.split('-'))
    if not (start_time <= current_time <= end_time):
        return jsonify({'error': 'Check-in not allowed at this time'}), 403

    attendance = Attendance(
        check_in_time=datetime.now(),
        course_id=course_id,
        ta_id=user_id
    )
    db.session.add(attendance)
    db.session.commit()

    return jsonify({'message': 'Checked in successfully'}), 200


# Check-out
@app.route('/check-out', methods=['POST'])
def check_out():
    user_id = request.json.get('user_id')
    attendance_id = request.json.get('attendance_id')

    if not user_id or not attendance_id:
        return jsonify({'error': 'Missing user_id or attendance_id'}), 400

    attendance = Attendance.query.get(attendance_id)
    if not attendance or attendance.ta_id != user_id:
        return jsonify({'error': 'Attendance record not found or user mismatch'}), 404

    attendance.check_out_time = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Checked out successfully'}), 200


# Verify attendance
@app.route('/verify-attendance', methods=['POST'])
def verify_attendance():
    teacher_id = request.json.get('teacher_id')
    attendance_id = request.json.get('attendance_id')

    if not teacher_id or not attendance_id:
        return jsonify({'error': 'Missing teacher_id or attendance_id'}), 400

    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404

    course = attendance.course
    if not course or course.teacher_id != teacher_id:
        return jsonify({'error': 'Course not found or teacher mismatch'}), 404

    attendance.verified_by_teacher = True
    db.session.commit()

    return jsonify({'message': 'Attendance verified successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)

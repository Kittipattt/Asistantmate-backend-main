from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.course_service import CourseService

course_bp = Blueprint('course_controller', __name__)
course_service = CourseService()

@course_bp.route('/api/courses', methods=['GET'])
def get_courses():
    response = course_service.get_courses()
    return jsonify(response), response.get('status', 200)

@course_bp.route('/api/my_courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    identity = get_jwt_identity()
    response = course_service.get_my_courses(identity['username'])
    return jsonify(response), response.get('status', 200)

@course_bp.route('/api/teacher_courses', methods=['GET'])
@jwt_required()
def get_teacher_courses():
    identity = get_jwt_identity()
    response = course_service.get_teacher_courses(identity['Teacher_name'])
    return jsonify(response), response.get('status', 200)

@course_bp.route('/api/ta_for_course', methods=['GET'])
@jwt_required()
def get_tas_for_course():
    course_id = request.args.get('course_id')
    response = course_service.get_tas_for_course(course_id)
    return jsonify(response), response.get('status', 200)


@course_bp.route('/api/course_sections/<course_id>', methods=['GET'])
def get_course_sections(course_id):
    """
    Fetches sections for a given course ID.
    """
    response = course_service.get_course_sections(course_id)

    # If response is a list, return it as a successful response.
    if isinstance(response, list):
        return jsonify(response), 200

    # If response is a dictionary (error message), return it with the appropriate status.
    return jsonify(response), response.get('status', 500)


@course_bp.route('/api/course_tas/<course_id>/<section>', methods=['GET'])
def get_course_tas(course_id, section):
    """
    Fetches TAs for a given course ID and section.
    """
    response = course_service.get_course_tas(course_id, section)

    # If response is a list, return it as a successful response.
    if isinstance(response, list):
        return jsonify(response), 200

    # If response is a dictionary (error message), return it with the appropriate status.
    return jsonify(response), response.get('status', 500)
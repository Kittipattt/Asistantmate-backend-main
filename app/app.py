import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import mysql.connector
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import secrets

from mysql.connector import errorcode
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

CORS(app, supports_credentials=True)

JWT_SECRET_KEY = secrets.token_urlsafe(32)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
jwt = JWTManager(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Ice15088",
        database="amdata",
        port=3306,
    )


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,DELETE,PUT'
    return response


@app.route('/api/courses', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT *
        FROM course_data01
        INNER JOIN amdata.ta_data ON amdata.course_data01.ta_id = amdata.ta_data.ta_id
        INNER JOIN amdata.teacher_data ON amdata.course_data01.Teacher_id = amdata.teacher_data.Teacher_id
    ''')
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


@app.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def login():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM ta_data WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    try:
        if user:
            session['user'] = user['username']
            access_token = create_access_token(identity={"username": user['username']})
            return jsonify({"message": "Login successful", "user": user, "access_token": access_token}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    finally:
        cursor.close()
        connection.close()


@app.route('/login_teacher', methods=['POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def login_teacher():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    teacher_name = data.get('Teacher_name')
    password = data.get('password')

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM teacher_data WHERE Teacher_name = %s AND password = %s"
    cursor.execute(query, (teacher_name, password))
    user = cursor.fetchone()

    if user:
        session['user'] = user['Teacher_name']
        access_token = create_access_token(identity={"Teacher_name": user['Teacher_name']})
        return jsonify({"message": "Login successful", "user": user, "access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid Teacher_name or password"}), 401


@app.route('/api/student_login', methods=['POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def student_login():
    con = get_db_connection()
    if con is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM student_data WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    try:
        if user:
            session['user'] = user['username']
            access_token = create_access_token(identity={"username": user['username']})
            return jsonify({"message": "Login successful", "user": user, "access_token": access_token}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    finally:
        cursor.close()
        con.close()


@app.route('/api/admin_login', methods=['POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def admin_login():
    con = get_db_connection()
    if con is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM admin_data WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()

    try:
        if admin:
            session['admin'] = admin['username']
            access_token = create_access_token(identity={"username": admin['username'], "name": admin['name']})
            return jsonify(
                {"message": "Login successful", "admin": {"username": admin['username'], "name": admin['name']},
                 "access_token": access_token}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    finally:
        cursor.close()
        con.close()


@app.route('/api/my_courses', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_my_courses():
    identity = get_jwt_identity()
    username = identity.get('username')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT course_data01.*, teacher_data.Teacher_name
        FROM course_data01
        JOIN teacher_data ON course_data01.Teacher_id = teacher_data.Teacher_id
        WHERE ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
    ''', (username,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


@app.route('/api/teacher_courses', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_teacher_courses():
    identity = get_jwt_identity()
    teacher_name = identity.get('Teacher_name')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT course_data01.*, teacher_data.Teacher_name
        FROM course_data01
        JOIN teacher_data ON course_data01.Teacher_id = teacher_data.Teacher_id
        WHERE course_data01.Teacher_id = (SELECT Teacher_id FROM teacher_data WHERE Teacher_name = %s)
    ''', (teacher_name,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


@app.route('/api/cancel_class', methods=['POST'])
def cancel_class():
    data = request.json

    course_id = data.get('course_id')
    cancelled_date = data.get('cancelled_date')
    cancellation_reason = data.get('cancellation_reason')

    if not course_id or not cancelled_date:
        return jsonify({'message': 'Missing required data'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO cancel (course_id, cancelled_date, cancellation_reason)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (course_id, cancelled_date, cancellation_reason))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Class cancelled successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to cancel class', 'error': str(e)}), 500


@app.route('/api/current_user', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_current_user():
    identity = get_jwt_identity()
    username = identity.get('username')
    return jsonify({"username": username})


@app.route('/api/current_teacher', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_current_teacher():
    identity = get_jwt_identity()
    Teacher_name = identity.get('Teacher_name')
    return jsonify({"Teacher_name": Teacher_name})


@app.route('/api/checkin', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def check_in():
    user_identity = get_jwt_identity()
    username = user_identity.get('username')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()

    try:
        cursor.execute('SELECT ta_id FROM ta_data WHERE username = %s', (username,))
        ta_data = cursor.fetchone()

        if ta_data:
            ta_id = ta_data['ta_id']
            course_id = data['course_id']

            cursor.fetchall()

            cursor.execute('SELECT course_type FROM course_data01 WHERE courseid = %s', (course_id,))
            course_data = cursor.fetchone()

            if course_data:
                course_type = course_data['course_type']

                cursor.fetchall()

                cursor.execute('''
                    INSERT INTO attendance (ta_id, course_id, date, start_time, end_time, status, course_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (ta_id, course_id, data['date'], data['startTime'], data['endTime'], 'Present', course_type))
                conn.commit()

                return jsonify({'message': 'Attendance checked in successfully.'}), 200
            else:
                return jsonify({'message': 'Course not found.'}), 404
        else:
            return jsonify({'message': 'User not found.'}), 404

    except mysql.connector.Error as error:
        return jsonify({'message': 'Failed to check in attendance.', 'error': str(error)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/attendance', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
def get_attendance():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT * FROM attendance')
        attendance = cursor.fetchall()

        for record in attendance:
            record['start_time'] = str(record['start_time'])
            record['end_time'] = str(record['end_time'])

        return jsonify({'attendance': attendance}), 200
    except mysql.connector.Error as error:
        return jsonify({'message': 'Failed to fetch attendance.', 'error': str(error)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/viewattendance', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def viewattendance():
    try:
        identity = get_jwt_identity()
        username = identity.get('username')

        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT * 
                    FROM attendance 
                    WHERE ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
                ''', (username,))
                attendance_records = cursor.fetchall()

                for record in attendance_records:
                    for time_field in ['start_time', 'end_time']:
                        if isinstance(record[time_field], timedelta):
                            total_seconds = record[time_field].total_seconds()
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            record[time_field] = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

                    if isinstance(record['date'], datetime):
                        record['date'] = record['date'].strftime('%Y-%m-%d')

                return jsonify({'attendance': attendance_records}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        error_msg = {
            errorcode.ER_ACCESS_DENIED_ERROR: "Something is wrong with your user name or password.",
            errorcode.ER_BAD_DB_ERROR: "Database does not exist."
        }.get(err.errno, str(err))
        return jsonify({'error': error_msg}), 500


@app.route('/api/course_sections/<course_id>', methods=['GET'])
def get_course_sections(course_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT section FROM course_data01 
            WHERE courseid = %s
        """, (course_id,))
        sections = cursor.fetchall()
        return jsonify(sections), 200
    except mysql.connector.Error as err:
        return jsonify({'message': f"Error: {err}"}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/courses', methods=['GET'])
def get_all_courses():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT courseid, course_name FROM course_data01
        """)
        courses = cursor.fetchall()
        return jsonify(courses), 200
    except mysql.connector.Error as err:
        return jsonify({'message': f"Error: {err}"}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/course_tas/<course_id>/<section>', methods=['GET'])
def get_course_tas(course_id, section):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ta_data.ta_id, ta_data.ta_name 
            FROM course_data01 
            JOIN ta_data ON course_data01.ta_id = ta_data.ta_id 
            WHERE course_data01.courseid = %s AND course_data01.section = %s
        """, (course_id, section))
        tas = cursor.fetchall()
        return jsonify(tas), 200
    except mysql.connector.Error as err:
        return jsonify({'message': f"Error: {err}"}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/evaluate_ta', methods=['POST'])
def evaluate_ta():
    data = request.json
    name = data.get('name')
    course_id = data.get('course')
    section = data.get('section')
    ta_name = data.get('taName')
    score = data.get('score')
    comment = data.get('comment')

    if not all([name, course_id, section, ta_name, score, comment]):
        return jsonify({'message': 'Please fill in all fields'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO ta_evaluations (name, course_id, section, ta_name, score, comment) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, course_id, section, ta_name, score, comment)
        )
        connection.commit()

        return jsonify({'message': 'Evaluation submitted successfully'}), 200
    except mysql.connector.Error as err:
        app.logger.error(f"Error: {err}")
        return jsonify({'message': f"Error: {err}"}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/evaluate_results', methods=['POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def evaluate_results():
    con = get_db_connection()
    if con is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.get_json()
    ta_name = data.get('ta_name')

    cursor = con.cursor(dictionary=True)
    try:
        # Query to get teacher evaluations
        cursor.execute("""
            SELECT * FROM evaluate WHERE ta_name = %s
        """, (ta_name,))
        teacher_evaluations = cursor.fetchall()

        # Query to get student evaluations
        cursor.execute("""
            SELECT * FROM student_evaluate WHERE ta_name = %s
        """, (ta_name,))
        student_evaluations = cursor.fetchall()

        return jsonify({
            "teacher_evaluations": teacher_evaluations,
            "student_evaluations": student_evaluations
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        con.close()


@app.route('/api/get_tas', methods=['GET'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def get_tas():
    con = get_db_connection()
    if con is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = con.cursor(dictionary=True)
    try:
        # Query to get distinct TA names from both tables
        cursor.execute("""
            SELECT DISTINCT ta_name FROM evaluate
            UNION
            SELECT DISTINCT ta_name FROM student_evaluate
        """)
        ta_names = cursor.fetchall()

        return jsonify({"tas": [ta['ta_name'] for ta in ta_names]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        con.close()



if __name__ == '__main__':
    app.run(debug=True)

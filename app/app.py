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
        passwd="201245",
        database="AMData",
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
    connection = None
    cursor = None
    try:
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

    except mysql.connector.Error as err:
        return jsonify({"error": f"MySQL error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/api/ta_for_course', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_tas_for_course():
    course_id = request.args.get('course_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT ta_id, ta_name
        FROM ta_data
        WHERE ta_id IN (SELECT ta_id FROM course_data01 WHERE courseid = %s)
    ''', (course_id,))
    tas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"tas": tas})


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


@app.route('/api/attendance_summary', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_attendance_summary():
    try:
        identity = get_jwt_identity()
        username = identity.get('username')

        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Ensure no duplicate records by using DISTINCT or a GROUP BY clause
                cursor.execute('''
                    SELECT DISTINCT
                        a.course_id, a.date, a.start_time, a.end_time,
                        t.ta_name, c.course_type,
                        TIMESTAMPDIFF(MINUTE, a.start_time, a.end_time) AS minutes_worked
                    FROM attendance a
                    JOIN ta_data t ON a.ta_id = t.ta_id
                    JOIN course_data01 c ON a.course_id = c.courseid
                    WHERE a.ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
                ''', (username,))
                attendance_records = cursor.fetchall()

                # Define wage rates based on course_type
                wage_rates = {
                    'stu_thai': 90,
                    'stu_inter': 120,
                    'grad_thai': 200,
                    'grad_inter': 300,
                    'lecturer': 450
                }

                for record in attendance_records:
                    # Convert minutes to hours and minutes format
                    minutes_worked = record['minutes_worked']
                    hours = minutes_worked // 60
                    minutes = minutes_worked % 60
                    record['hours_worked'] = f'{hours}h {minutes}m'

                    # Convert datetime objects to strings
                    if isinstance(record['date'], datetime):
                        record['date'] = record['date'].strftime('%Y-%m-%d')

                    # Format time fields
                    for time_field in ['start_time', 'end_time']:
                        if isinstance(record[time_field], timedelta):
                            total_seconds = record[time_field].total_seconds()
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            record[time_field] = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

                    # Calculate wage based on course_type
                    course_type = record['course_type']
                    rate_per_hour = wage_rates.get(course_type, 0)
                    record['wage'] = f'{rate_per_hour * (minutes_worked / 60):.2f}'

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


@app.route('/api/evaluate', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def submit_evaluation():
    data = request.get_json()
    identity = get_jwt_identity()
    teacher_name = identity.get('Teacher_name')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO evaluate (ta_name, ta_id, score, comment, evaluate_date, Teacher_name, course_id)
            VALUES (
                (SELECT ta_name FROM ta_data WHERE ta_id = %s),
                %s, %s, %s, NOW(), %s, %s
            )
        ''', (
            data['ta_id'], data['ta_id'], data['score'], data['comment'], teacher_name, data['course_id']
        ))
        conn.commit()
        return jsonify({"status": "success"}), 201
    except mysql.connector.Error as error:
        return jsonify({'message': 'Failed to submit evaluation.', 'error': str(error)}), 500
    finally:
        cursor.close()
        conn.close()


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

        # Query to get student evaluations from ta_evaluations
        cursor.execute("""
            SELECT * FROM ta_evaluations WHERE ta_name = %s
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
            SELECT DISTINCT ta_name FROM ta_evaluations
        """)
        ta_names = cursor.fetchall()

        return jsonify({"tas": [ta['ta_name'] for ta in ta_names]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        con.close()


@app.route('/api/get_ta_status', methods=['GET'])
@jwt_required()
def get_ta_status():
    current_user = get_jwt_identity()  # Extract user information from the JWT token
    username = current_user['username']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to get TA status
    query = "SELECT ta_status FROM ta_data WHERE username = %s"
    cursor.execute(query, (username,))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        return jsonify({'ta_status': result['ta_status']})
    else:
        return jsonify({'message': 'TA status not found'}), 404


from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route('/api/ta_notifications', methods=['GET'])
@jwt_required()
def get_ta_notifications():
    try:
        # Get the identity from the JWT token
        identity = get_jwt_identity()

        # Extract the username from the identity dictionary
        username = identity.get('username')

        if not username:
            return jsonify({"error": "User not authenticated"}), 401

        # Fetch the TA ID based on the username
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        ta_query = "SELECT ta_id FROM ta_data WHERE username = %s"
        cursor.execute(ta_query, (username,))
        ta = cursor.fetchone()

        if ta is None:
            return jsonify({"error": "TA not found"}), 404

        ta_id = int(ta['ta_id'])

        # SQL query to fetch cancellations related to the TA's courses
        query = """
        SELECT c.cancel_id, c.course_id, c.cancelled_date, c.cancellation_reason, c.created_at
        FROM cancel c
        JOIN course_data01 cd ON c.course_id = cd.courseid
        WHERE cd.ta_id = %s
        """

        # Execute the query with the TA's ID
        cursor.execute(query, (ta_id,))
        cancellations = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Return the results as JSON
        return jsonify(cancellations), 200

    except Exception as e:
        # Log the error and return a 500 Internal Server Error response
        print(f"Error fetching TA notifications: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


def timedelta_to_str(td):
    """Convert timedelta to a string representation (e.g., total seconds)."""
    if isinstance(td, timedelta):
        return str(td.total_seconds())
    return td


def datetime_to_str(dt):
    """Convert datetime to a string representation."""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


logging.basicConfig(level=logging.DEBUG)


@app.route('/api/teacher_notifications', methods=['GET'])
@jwt_required()
def get_teacher_notifications():
    cursor = None
    connection = None
    try:
        current_user = get_jwt_identity()
        teacher_name = current_user.get("Teacher_name")

        if not teacher_name:
            return jsonify({"error": "No teacher logged in"}), 401

        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        query = "SELECT Teacher_id FROM teacher_data WHERE Teacher_name = %s"
        cursor.execute(query, (teacher_name,))
        teacher = cursor.fetchone()

        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404

        teacher_id = teacher['Teacher_id']

        query = """
        SELECT DISTINCT a.id, a.ta_id, a.course_id, a.date, a.start_time, a.end_time, a.status, a.course_type
        FROM attendance a
        JOIN course_data01 c ON a.course_id = c.courseid
        WHERE c.Teacher_id = %s
        """
        cursor.execute(query, (teacher_id,))
        notifications = cursor.fetchall()

        logging.debug(f"Fetched notifications from database: {notifications}")

        for notification in notifications:
            notification['date'] = datetime_to_str(notification.get('date'))
            notification['start_time'] = timedelta_to_str(notification.get('start_time'))
            notification['end_time'] = timedelta_to_str(notification.get('end_time'))

        logging.debug(f"Processed notifications: {notifications}")

        return jsonify(notifications), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"MySQL error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/api/approve_notification', methods=['POST'])
@jwt_required()
def approve_notification():
    try:
        # Fetch the logged-in teacher's ID from the JWT token
        current_user = get_jwt_identity()
        teacher_name = current_user.get("Teacher_name")

        # Validate that the teacher is logged in
        if not teacher_name:
            return jsonify({"error": "No teacher logged in"}), 401

        # Connect to the database
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()

        # Get the notification ID from the request
        notification_id = request.json.get('id')

        # Update the notification status to "Approved"
        query = "UPDATE attendance SET status = 'Approved' WHERE id = %s"
        cursor.execute(query, (notification_id,))
        connection.commit()

        return jsonify({"message": "Notification approved"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"MySQL error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/api/reject_notification', methods=['POST'])
def reject_notification():
    data = request.get_json()
    notification_id = data.get('id')

    # Validate the notification_id
    if not notification_id:
        return jsonify({"error": "Invalid notification ID"}), 400

    # Perform deletion from the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM attendance WHERE id = %s', (notification_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Notification deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

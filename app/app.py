import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import mysql.connector
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import secrets

from mysql.connector import errorcode

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


@app.route('/api/register', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ta_name = data.get('ta_name')
    ta_status = data.get('ta_status')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = "INSERT INTO ta_data (username, password, ta_name, ta_status) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (username, password, ta_name, ta_status))
        conn.commit()
        return jsonify({'message': 'Registered successfully'}), 201
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        conn.rollback()
        return jsonify({"message": "Failed to register user"}), 500
    finally:
        cursor.close()
        conn.close()


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


@app.route('/api/my_courses', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_my_courses():
    identity = get_jwt_identity()
    username = identity.get('username')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM course_data01
        WHERE ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
    ''', (username,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


@app.route('/api/current_user', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
@jwt_required()
def get_current_user():
    identity = get_jwt_identity()
    username = identity.get('username')
    return jsonify({"username": username})


@app.route('/api/checkin', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def check_in():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()

    try:
        cursor.execute('''
            INSERT INTO attendance (course_id, date, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data['course_id'], data['date'], data['startTime'], data['endTime'], 'Present'))
        conn.commit()
        return jsonify({'message': 'Attendance checked in successfully.'}), 200
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
        return jsonify({'attendance': attendance}), 200
    except mysql.connector.Error as error:
        return jsonify({'message': 'Failed to fetch attendance.', 'error': str(error)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/viewattendance', methods=['GET'])
@cross_origin(origin='http://localhost:3000')
def viewattendance():
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM attendance")
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


if __name__ == '__main__':
    app.run(debug=True)

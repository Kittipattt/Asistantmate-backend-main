import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import secrets
from flask import session

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

CORS(app, supports_credentials=True)

JWT_SECRET_KEY = secrets.token_urlsafe(32)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
jwt = JWTManager(app)


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="201245",
        database="AMData",
        port=3306,
    )
    return connection


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route("/api/ta/check_attendance", methods=["POST"])
@cross_origin()
def check_attendance():
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    start_time_str = now.strftime('%H:%M:%S')
    end_time_str = (now + timedelta(minutes=90)).strftime('%H:%M:%S')
    user_id = request.json.get('userId')  # Assuming userId is sent in the request
    course_id = request.json.get('courseId')  # Assuming courseId is sent in the request

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert attendance
        sql = "INSERT INTO attendance (date, start_time, end_time, userId, courseId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (date_str, start_time_str, end_time_str, user_id, course_id))
        conn.commit()

        # Insert notification
        notification_sql = "INSERT INTO notifications (user_id, message, status) VALUES (%s, %s, %s)"
        cursor.execute(notification_sql,
                       (user_id, "Attendance recorded successfully. Waiting for approval.", "pending"))
        conn.commit()

        return jsonify({"message": "Attendance recorded successfully"}), 201
    except Exception as e:
        logging.error(f"Error checking attendance: {str(e)}")
        conn.rollback()
        return jsonify({"message": "Failed to record attendance"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
           SELECT *
           FROM course_data
           INNER JOIN AMData.ta_data ON AMData.course_data.ta_id = AMData.ta_data.ta_id
           INNER JOIN AMData.teacher_data ON AMData.course_data.Teacher_id = AMData.teacher_data.Teacher_id
       ''')
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql, (data['username'], hashed_password, data['role']))
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

    if user:
        session['user'] = user['username']
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401



@app.route('/api/my_courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    identity = get_jwt_identity()
    ta_id = identity.get('ta_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM course_data
        WHERE ta_id = %s
    ''', (ta_id,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"courses": courses})


if __name__ == '__main__':
    app.run(debug=True)

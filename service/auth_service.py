from utils.db import get_db_connection
from flask_jwt_extended import create_access_token
from flask import session


class AuthService:

    def login(self, data):
        connection = get_db_connection()
        if connection is None:
            return {"error": "Database connection failed", "status": 500}

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
                return {"message": "Login successful", "user": user, "access_token": access_token, "status": 200}
            else:
                return {"error": "Invalid username or password", "status": 401}
        finally:
            cursor.close()
            connection.close()

    def login_teacher(self, data):
        connection = get_db_connection()
        if connection is None:
            return {"error": "Database connection failed", "status": 500}

        teacher_name = data.get('Teacher_name')
        password = data.get('password')

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM teacher_data WHERE Teacher_name = %s AND password = %s"
        cursor.execute(query, (teacher_name, password))
        user = cursor.fetchone()

        try:
            if user:
                session['user'] = user['Teacher_name']
                access_token = create_access_token(identity={"Teacher_name": user['Teacher_name']})
                return {"message": "Login successful", "user": user, "access_token": access_token, "status": 200}
            else:
                return {"error": "Invalid Teacher_name or password", "status": 401}
        finally:
            cursor.close()
            connection.close()

    def student_login(self, data):
        connection = get_db_connection()
        if connection is None:
            return {"error": "Database connection failed", "status": 500}

        username = data.get('username')
        password = data.get('password')

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM student_data WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        try:
            if user:
                session['user'] = user['username']
                access_token = create_access_token(identity={"username": user['username']})
                return {"message": "Login successful", "user": user, "access_token": access_token, "status": 200}
            else:
                return {"error": "Invalid username or password", "status": 401}
        finally:
            cursor.close()
            connection.close()

    def admin_login(self, data):
        connection = get_db_connection()
        if connection is None:
            return {"error": "Database connection failed", "status": 500}

        username = data.get('username')
        password = data.get('password')

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admin_data WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        admin = cursor.fetchone()

        try:
            if admin:
                session['admin'] = admin['username']
                access_token = create_access_token(identity={"username": admin['username'], "name": admin['name']})
                return {"message": "Login successful", "admin": {"username": admin['username'], "name": admin['name']},
                        "access_token": access_token, "status": 200}
            else:
                return {"error": "Invalid username or password", "status": 401}
        finally:
            cursor.close()
            connection.close()

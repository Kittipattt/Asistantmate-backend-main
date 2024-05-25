import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_cors import CORS, cross_origin
import mysql.connector

app = Flask(__name__)
CORS(app)


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="201245",
        database="AMData",
        port=3306,
    )
    return connection


def reset_attendance_table():
    """Function to reset the attendance table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance")  # Clears the table
    conn.commit()
    cursor.close()
    conn.close()
    print("Attendance table reset.")

@app.route("/api/ta/check_attendance", methods=["POST"])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def check_attendance():
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    start_time_str = now.strftime('%H:%M:%S')
    end_time_str = (now + timedelta(minutes=30)).strftime('%H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO attendance (date, start_time, end_time) VALUES (%s, %s, %s)"
    cursor.execute(sql, (date_str, start_time_str, end_time_str))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Attendance recorded successfully"}), 201

@app.route('/api/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) FROM AMData.course_data;')
    total = cursor.fetchone()['COUNT(*)']

    cursor.execute('SELECT * FROM AMData.course_data LIMIT %s OFFSET %s;', (per_page, (page - 1) * per_page))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({
        "courses": courses,
        "total": total,
        "page": page,
        "per_page": per_page
    }), 200


if __name__ == '__main__':
    reset_attendance_table()
    app.run(debug=True)

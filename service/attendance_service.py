from utils.db import get_db_connection
from datetime import datetime, timedelta

class AttendanceService:

    def check_in(self, username, data):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch TA ID
            cursor.execute('SELECT ta_id FROM ta_data WHERE username = %s', (username,))
            ta_data = cursor.fetchone()
            if cursor._have_unread_result():
                cursor.fetchall()

            if not ta_data:
                return {'message': 'User not found.', 'status': 404}

            ta_id = ta_data['ta_id']
            course_id = data['course_id']

            # Fetch Course Type
            cursor.execute('SELECT course_type FROM course_data01 WHERE courseid = %s', (course_id,))
            course_data = cursor.fetchone()
            if cursor._have_unread_result():
                cursor.fetchall()

            if not course_data:
                return {'message': 'Course not found.', 'status': 404}

            course_type = course_data['course_type']

            # Insert attendance record
            cursor.execute('''
                INSERT INTO attendance (ta_id, course_id, date, start_time, end_time, status, course_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (ta_id, course_id, data['date'], data['startTime'], data['endTime'], 'Present', course_type))
            conn.commit()

            return {'message': 'Attendance checked in successfully.', 'status': 200}
        except Exception as error:
            return {'message': 'Failed to check in attendance.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def get_attendance(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM attendance')
            attendance = cursor.fetchall()

            for record in attendance:
                record['start_time'] = record['start_time'].strftime('%H:%M') if isinstance(record['start_time'], datetime) else record['start_time']
                record['end_time'] = record['end_time'].strftime('%H:%M') if isinstance(record['end_time'], datetime) else record['end_time']

            return {'attendance': attendance, 'status': 200}
        except Exception as error:
            return {'message': 'Failed to fetch attendance.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def view_attendance(self, username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT * 
                FROM attendance 
                WHERE ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
            ''', (username,))
            attendance_records = cursor.fetchall()

            # Format time and date
            for record in attendance_records:
                # If start_time or end_time is a timedelta, convert it to HH:MM format
                for time_field in ['start_time', 'end_time']:
                    if isinstance(record[time_field], timedelta):
                        total_seconds = record[time_field].total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        record[time_field] = f'{int(hours):02}:{int(minutes):02}'

                # Format the date
                if isinstance(record['date'], datetime):
                    record['date'] = record['date'].strftime('%Y-%m-%d')

            return {'attendance': attendance_records, 'status': 200}
        except Exception as error:
            return {'message': 'Failed to view attendance.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def get_attendance_summary(self, username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
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

            # Wage rates per course type
            wage_rates = {
                'stu_thai': 90,
                'stu_inter': 120,
                'grad_thai': 200,
                'grad_inter': 300,
                'lecturer': 450
            }

            for record in attendance_records:
                minutes_worked = record['minutes_worked']
                hours = minutes_worked // 60
                minutes = minutes_worked % 60
                record['hours_worked'] = f'{hours}h {minutes}m'

                # Format date and time
                if isinstance(record['date'], datetime):
                    record['date'] = record['date'].strftime('%Y-%m-%d')
                if isinstance(record['start_time'], timedelta):
                    total_seconds = record['start_time'].total_seconds()
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    record['start_time'] = f'{int(hours):02}:{int(minutes):02}'
                if isinstance(record['end_time'], timedelta):
                    total_seconds = record['end_time'].total_seconds()
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    record['end_time'] = f'{int(hours):02}:{int(minutes):02}'

                # Calculate wage based on course type and hours worked
                course_type = record['course_type']
                rate_per_hour = wage_rates.get(course_type, 0)
                record['wage'] = f'{rate_per_hour * (minutes_worked / 60):.2f}'

            return {'attendance': attendance_records, 'status': 200}
        except Exception as error:
            return {'message': 'Failed to fetch attendance summary.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def cancel_class(self, data):
        course_id = data.get('course_id')
        cancelled_date = data.get('cancelled_date')
        cancellation_reason = data.get('cancellation_reason')

        if not course_id or not cancelled_date:
            return {'message': 'Missing required data', 'status': 400}

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO cancel (course_id, cancelled_date, cancellation_reason)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (course_id, cancelled_date, cancellation_reason))

            conn.commit()
            return {'message': 'Class cancelled successfully', 'status': 200}

        except Exception as e:
            return {'message': 'Failed to cancel class', 'error': str(e), 'status': 500}

        finally:
            cursor.close()
            conn.close()

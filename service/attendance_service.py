from utils.db import get_db_connection
from datetime import timedelta, datetime


class AttendanceService:

    def check_in(self, username, data):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT ta_id FROM ta_data WHERE username = %s', (username,))
            ta_data = cursor.fetchone()

            if not ta_data:
                return {'message': 'User not found.', 'status': 404}

            ta_id = ta_data['ta_id']
            course_id = data['course_id']

            cursor.execute('SELECT course_type FROM course_data01 WHERE courseid = %s', (course_id,))
            course_data = cursor.fetchone()

            if not course_data:
                return {'message': 'Course not found.', 'status': 404}

            course_type = course_data['course_type']

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
                record['start_time'] = str(record['start_time'])
                record['end_time'] = str(record['end_time'])

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

            for record in attendance_records:
                for time_field in ['start_time', 'end_time']:
                    if isinstance(record[time_field], timedelta):
                        total_seconds = record[time_field].total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        record[time_field] = f'{int(hours):02}:{int(minutes):02}'

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

                if isinstance(record['date'], datetime):
                    record['date'] = record['date'].strftime('%Y-%m-%d')

                for time_field in ['start_time', 'end_time']:
                    if isinstance(record[time_field], timedelta):
                        total_seconds = record[time_field].total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        record[time_field] = f'{int(hours):02}:{int(minutes):02}'

                course_type = record['course_type']
                rate_per_hour = wage_rates.get(course_type, 0)
                record['wage'] = f'{rate_per_hour * (minutes_worked / 60):.2f}'

            return {'attendance': attendance_records, 'status': 200}
        except Exception as error:
            return {'message': 'Failed to fetch attendance summary.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

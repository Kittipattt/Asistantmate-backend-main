from utils.db import get_db_connection
from datetime import timedelta, datetime

class NotificationService:

    def get_ta_status(self, username):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            query = "SELECT ta_status FROM ta_data WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                return {'ta_status': result['ta_status'], 'status': 200}
            else:
                return {'message': 'TA status not found', 'status': 404}
        finally:
            cursor.close()
            connection.close()

    def get_ta_notifications(self, username):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ta_id FROM ta_data WHERE username = %s", (username,))
            ta = cursor.fetchone()

            if ta is None:
                return {'error': 'TA not found', 'status': 404}

            ta_id = int(ta['ta_id'])
            query = """
            SELECT c.cancel_id, c.course_id, c.cancelled_date, c.cancellation_reason, c.created_at
            FROM cancel c
            JOIN course_data01 cd ON c.course_id = cd.courseid
            WHERE cd.ta_id = %s
            """
            cursor.execute(query, (ta_id,))
            cancellations = cursor.fetchall()

            # Convert datetime fields to strings for JSON serialization
            for cancellation in cancellations:
                cancellation['cancelled_date'] = self.datetime_to_str(cancellation.get('cancelled_date'))
                cancellation['created_at'] = self.datetime_to_str(cancellation.get('created_at'))

            return {'cancellations': cancellations, 'status': 200}
        finally:
            cursor.close()
            connection.close()

    def get_teacher_notifications(self, teacher_name):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            # Fetch the teacher's ID using the teacher's name
            cursor.execute("SELECT Teacher_id FROM teacher_data WHERE Teacher_name = %s", (teacher_name,))
            teacher = cursor.fetchone()

            if not teacher:
                return {'error': 'Teacher not found', 'status': 404}

            teacher_id = teacher['Teacher_id']

            # Updated query to fetch the TA name by joining with the ta_data table
            query = """
            SELECT DISTINCT a.id, a.ta_id, a.course_id, c.course_name, a.date, a.start_time, a.end_time, a.status, a.course_type, t.ta_name
            FROM attendance a
            JOIN course_data01 c ON a.course_id = c.courseid
            JOIN ta_data t ON a.ta_id = t.ta_id
            WHERE c.Teacher_id = %s
            """
            cursor.execute(query, (teacher_id,))
            notifications = cursor.fetchall()

            # Convert datetime and timedelta fields to strings for JSON serialization
            for notification in notifications:
                notification['date'] = self.datetime_to_str(notification.get('date'))
                notification['start_time'] = self.timedelta_to_str(notification.get('start_time'))
                notification['end_time'] = self.timedelta_to_str(notification.get('end_time'))

            return {'notifications': notifications, 'status': 200}
        finally:
            cursor.close()
            connection.close()

    def approve_notification(self, notification_id, teacher_name):
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            query = "UPDATE attendance SET status = 'Approved' WHERE id = %s"
            cursor.execute(query, (notification_id,))
            connection.commit()

            return {'message': 'Notification approved', 'status': 200}
        finally:
            cursor.close()
            connection.close()
#12321
    def reject_notification(self, notification_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM attendance WHERE id = %s', (notification_id,))
            connection.commit()

            return {'message': 'Notification rejected', 'status': 200}
        finally:
            cursor.close()
            connection.close()

    # Helper method to convert timedelta to string (HH:MM)
    def timedelta_to_str(self, td):
        if isinstance(td, timedelta):
            total_seconds = td.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f'{int(hours):02}:{int(minutes):02}'
        return td

    # Helper method to convert datetime to string (ISO format)
    def datetime_to_str(self, dt):
        if isinstance(dt, datetime):
            return dt.strftime('%Y-%m-%d %H:%M:%S')  # You can adjust the format here
        return dt

from utils.db import get_db_connection


class CourseService:

    def get_courses(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT *
                FROM course_data01
                INNER JOIN ta_data ON course_data01.ta_id = ta_data.ta_id
                INNER JOIN teacher_data ON course_data01.Teacher_id = teacher_data.Teacher_id
            ''')
            courses = cursor.fetchall()
            return {'courses': courses, 'status': 200}
        finally:
            cursor.close()
            conn.close()

    def get_my_courses(self, username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT course_data01.*, teacher_data.Teacher_name
                FROM course_data01
                JOIN teacher_data ON course_data01.Teacher_id = teacher_data.Teacher_id
                WHERE ta_id = (SELECT ta_id FROM ta_data WHERE username = %s)
            ''', (username,))
            courses = cursor.fetchall()
            return {'courses': courses, 'status': 200}
        finally:
            cursor.close()
            conn.close()

    def get_teacher_courses(self, teacher_name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT course_data01.*, teacher_data.Teacher_name
                FROM course_data01
                JOIN teacher_data ON course_data01.Teacher_id = teacher_data.Teacher_id
                WHERE course_data01.Teacher_id = (SELECT Teacher_id FROM teacher_data WHERE Teacher_name = %s)
            ''', (teacher_name,))
            courses = cursor.fetchall()
            return {'courses': courses, 'status': 200}
        finally:
            cursor.close()
            conn.close()

    def get_tas_for_course(self, course_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT ta_id, ta_name
                FROM ta_data
                WHERE ta_id IN (SELECT ta_id FROM course_data01 WHERE courseid = %s)
            ''', (course_id,))
            tas = cursor.fetchall()
            return {'tas': tas, 'status': 200}
        finally:
            cursor.close()
            conn.close()

    def get_course_sections(self, course_id):
        """
        Fetches sections for a given course ID from the database.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT section FROM course_data01 WHERE courseid = %s"
            cursor.execute(query, (course_id,))
            sections = cursor.fetchall()

            if sections:
                return sections
            else:
                return {'message': 'No sections found for this course', 'status': 404}
        except Exception as e:
            return {'error': str(e), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def get_course_tas(self, course_id, section):
        """
        Fetches TAs for a given course ID and section from the database.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
               SELECT ta_data.ta_id, ta_data.ta_name
               FROM course_data01
               JOIN ta_data ON course_data01.ta_id = ta_data.ta_id
               WHERE course_data01.courseid = %s AND course_data01.section = %s
               """
            cursor.execute(query, (course_id, section))
            tas = cursor.fetchall()

            if tas:
                return tas
            else:
                return {'message': 'No TAs found for this course and section', 'status': 404}
        except Exception as e:
            return {'error': str(e), 'status': 500}
        finally:
            cursor.close()
            conn.close()
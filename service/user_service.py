from utils.db import get_db_connection

class UserService:

    def get_current_user(self, username):
        return {"username": username, "status": 200}

    def get_current_teacher(self, teacher_name):
        return {"Teacher_name": teacher_name, "status": 200}

    def get_tas(self):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT DISTINCT ta_name FROM evaluate
                UNION
                SELECT DISTINCT ta_name FROM ta_evaluations
            ''')
            ta_names = cursor.fetchall()
            return {"tas": [ta['ta_name'] for ta in ta_names], "status": 200}
        except Exception as error:
            return {"error": str(error), "status": 500}
        finally:
            cursor.close()
            connection.close()

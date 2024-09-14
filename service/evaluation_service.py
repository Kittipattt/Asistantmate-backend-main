from utils.db import get_db_connection


class EvaluationService:

    def evaluate_ta(self, data):
        name = data.get('name')
        course_id = data.get('course')
        section = data.get('section')
        ta_name = data.get('taName')
        score = data.get('score')
        comment = data.get('comment')

        if not all([name, course_id, section, ta_name, score, comment]):
            return {'message': 'Please fill in all fields', 'status': 400}

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO ta_evaluations (name, course_id, section, ta_name, score, comment) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, course_id, section, ta_name, score, comment))
            connection.commit()

            return {'message': 'Evaluation submitted successfully', 'status': 200}
        except Exception as err:
            return {'message': f'Error: {str(err)}', 'status': 500}
        finally:
            cursor.close()
            connection.close()

    def submit_evaluation(self, data, teacher_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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

            return {"status": "success", 'status': 201}
        except Exception as error:
            return {'message': 'Failed to submit evaluation.', 'error': str(error), 'status': 500}
        finally:
            cursor.close()
            conn.close()

    def get_evaluation_results(self, ta_name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT * FROM evaluate WHERE ta_name = %s
            ''', (ta_name,))
            teacher_evaluations = cursor.fetchall()

            cursor.execute('''
                SELECT * FROM ta_evaluations WHERE ta_name = %s
            ''', (ta_name,))
            student_evaluations = cursor.fetchall()

            return {
                "teacher_evaluations": teacher_evaluations,
                "student_evaluations": student_evaluations,
                "status": 200
            }
        except Exception as e:
            return {"error": str(e), 'status': 500}
        finally:
            cursor.close()
            conn.close()

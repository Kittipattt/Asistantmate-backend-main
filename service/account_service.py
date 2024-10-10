from utils.db import get_db_connection

class AccountService:

    def change_username(self, current_username, new_username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if the new username is already taken
            cursor.execute('SELECT username FROM ta_data WHERE username = %s', (new_username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return {"message": "Username already taken", "status": 400}

            # Update the username
            cursor.execute('UPDATE ta_data SET username = %s WHERE username = %s', (new_username, current_username))
            conn.commit()

            return {"message": 'Username changed successfully', 'new_username': new_username, 'status': 200}

        except Exception as e:
            return {"error": str(e), "status": 500}

        finally:
            cursor.close()
            conn.close()

    def change_password(self, username, new_password):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Here, you should ideally hash the new password before saving it
            cursor.execute('UPDATE ta_data SET password = %s WHERE username = %s', (new_password, username))
            conn.commit()

            return {"message": 'Password changed successfully', 'status': 200}

        except Exception as e:
            return {"error": str(e), "status": 500}

        finally:
            cursor.close()
            conn.close()

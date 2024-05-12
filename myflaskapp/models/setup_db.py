from myflaskapp.models import User
from myflaskapp.models.database import db


def create_user(username, email, password, role='ta'):
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


# Example usage
if __name__ == '__main__':
    create_user('adminuser', 'admin@example.com', 'securepassword', 'admin')
    create_user('teacheruser', 'teacher@example.com', 'securepassword', 'teacher')
    create_user('tauser', 'ta@example.com', 'securepassword', 'ta')

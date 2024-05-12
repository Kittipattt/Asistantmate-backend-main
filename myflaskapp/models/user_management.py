from myflaskapp.models import User
from myflaskapp.models.database import db


def create_user(username, email, password, role='ta'):
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

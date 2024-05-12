from sqlalchemy import event
from .User import User
from .database import db, Course


@event.listens_for(User.__table__, 'after_create')
def create_default_user(*args, **kwargs):
    user1 = User(username='IhereLing', email='LingInwZa@gmail.com', role="Ling")
    db.session.add(user1)
    db.session.commit()



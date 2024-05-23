# models/course.py

from app import db


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Assuming a User model for teacher

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
# models/cancelled_class.py

from app import db
from datetime import datetime


class CancelledClass(db.Model):
    __tablename__ = 'cancelled_classes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    cancellation_date = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', backref=db.backref('cancelled_classes', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else "",
            "cancellation_date": self.cancellation_date.strftime("%Y-%m-%d")
        }

# models/attendance.py

from app import db
from datetime import datetime


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)  # Assuming you have a user_id to track which user attended

    def to_dict(self):
        """
        Convert the Attendance instance into a dictionary format.
        """
        return {
            "id": self.id,
            "course_id": self.course_id,
            "date_time": self.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id
        }

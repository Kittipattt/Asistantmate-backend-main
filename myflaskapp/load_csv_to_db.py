import pandas as pd
from app import db
from models import Course
from app import app


def load_data():
    df = pd.read_csv('resource/course_data.csv')
    with app.app_context():
        db.create_all()  # Create database tables based on models
        for _, row in df.iterrows():
            course = Course(
                course_name=row['CourseName'],
                course_code=row['CourseId'],
                major=row.get('major', ''),
                section=row.get('section', '')
            )
            db.session.add(course)
        db.session.commit()


if __name__ == '__main__':
    load_data()

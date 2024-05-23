from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from api.attendance import attendance_api
from api.auth import auth_api
from api.disbursement import disbursement_api
from api.evaluation import evaluation_api
from api.notification import notification_api
from api.profile import profile_api
from api.wages import wages_api
from flask_cors import CORS  # Import CORS if you need cross-origin requests

from api.cancellation import cancellation_api
from models.course import Course
from models.cancelled_class import CancelledClass

# Initialize SQLAlchemy with no parameters
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configurations can be loaded here from a config.py or directly
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(attendance_api, url_prefix='/api/attendance')
    app.register_blueprint(auth_api, url_prefix='/api/auth')
    app.register_blueprint(disbursement_api, url_prefix='/api/disbursement')
    app.register_blueprint(evaluation_api, url_prefix='/api/evaluation')
    app.register_blueprint(notification_api, url_prefix='/api/notification')
    app.register_blueprint(profile_api, url_prefix='/api/profile')
    app.register_blueprint(wages_api, url_prefix='/api/wages')
    app.register_blueprint(cancellation_api, url_prefix='/api/cancellation')

    @app.route('/cancel_class_view')
    def cancel_class_view():
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return "Teacher ID is required to view the cancellation page", 400

        try:
            courses = Course.query.filter_by(teacher_id=teacher_id).all()
        except Exception as e:
            return f"Failed to load courses: {e}", 500

        return render_template('cancel_class.html', courses=courses) #เปลี่ยนที่ขีดสีเหลืองเป็นหน้าที่อยากให้ใช้

    # Enable CORS if needed, can be limited to specific routes or origins
    CORS(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

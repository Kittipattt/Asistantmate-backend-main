from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS if you need cross-origin requests

# Initialize SQLAlchemy at the global scope
db = SQLAlchemy()


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Application configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS globally for all domains

    # Import models here to avoid circular imports
    from models.course import Course
    from models.cancelled_class import CancelledClass

    # Register blueprints
    from api.attendance import attendance_api
    app.register_blueprint(attendance_api, url_prefix='/api/attendance')

    from api.notification import notification_api
    app.register_blueprint(notification_api, url_prefix='/api/notification')

    from api.cancellation import cancellation_api
    app.register_blueprint(cancellation_api, url_prefix='/api/cancellation')

    @app.route('/cancel_class_view')
    def cancel_class_view():
        """View handler for cancellation page."""
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return "Teacher ID is required to view the cancellation page", 400

        try:
            courses = Course.query.filter_by(teacher_id=teacher_id).all()
        except Exception as e:
            return f"Failed to load courses: {e}", 500

        return render_template('cancel_class.html', courses=courses)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

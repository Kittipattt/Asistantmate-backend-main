from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Import blueprints from controller
from controller.user_controller import user_bp
from controller.notification_controller import notification_bp
from controller.attendance_controller import attendance_bp
from controller.auth_controller import auth_bp
from controller.evaluation_controller import evaluation_bp
from controller.course_controller import course_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Replace with actual secret key
jwt = JWTManager(app)

# Register blueprints (controller)
app.register_blueprint(user_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(evaluation_bp)
app.register_blueprint(course_bp)

if __name__ == '__main__':
    app.run(debug=True)

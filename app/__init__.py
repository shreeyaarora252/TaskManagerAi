from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()  

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Load all config, including JWT_SECRET_KEY

    # Enable extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # ✅ Initialize JWTManager with the app

    # Import models to register them with SQLAlchemy
    from app.models.user import User
    from app.models.task import Task

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.subtasks import subtasks_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(subtasks_bp, url_prefix='/subtasks')

    return app

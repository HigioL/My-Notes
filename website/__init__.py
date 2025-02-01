from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate  # Import Flask-Migrate

db = SQLAlchemy()
migrate = Migrate()  # Initialize Flask-Migrate here (outside create_app)
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)  
    app.config['SECRET_KEY'] = 'AVHIUAHVEA'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Add this line to suppress a warning

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app

    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models
    from .models import User, Note, Post, Comment

    # Initialize the database within app context
    with app.app_context():
        db.create_all()  # This is optional since Flask-Migrate will handle schema updates
        print('Database Created')

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
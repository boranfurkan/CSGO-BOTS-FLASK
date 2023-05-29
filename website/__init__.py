from flask import Flask
from website.db.db import db, DB_NAME
from flask_login import LoginManager
from .web_socket import socketio
from os import path


def create_app():
    # Create a Flask web server from the Flask module
    app = Flask(__name__)
    # Enable debugging mode
    app.config["DEBUG"] = True
    # Set secret key for session management
    app.config['SECRET_KEY'] = 'realscretkey'
    # Set the SQLALCHEMY_DATABASE_URI key to define the connection to our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # Initialize SQLAlchemy with Flask's app
    db.init_app(app)

    # Import the views module and the auth module
    from .views import views
    from .auth import auth

    # Register the blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import the User model
    from .models import User

    # Create all the database tables within the app context
    with app.app_context():
        db.create_all()

    # Setup Flask-Login
    login_manager = LoginManager()
    # Set the name of the login view that lets user login
    login_manager.login_view = 'auth.login'
    # Initialize it
    login_manager.init_app(app)

    # This callback is used to reload the user object from the user ID stored in the session.
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Initialize Flask-SocketIO with the app
    socketio.init_app(app)

    # Return the app instance.
    return app


def create_database(app):
    # Check if the database specified in DB_NAME exists, if not, create one
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

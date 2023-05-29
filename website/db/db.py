# Import the SQLAlchemy module from the flask_sqlalchemy package. SQLAlchemy is an Object-Relational Mapping (ORM)
# tool in Python, which gives your application a high-level, Pythonic interface to a relational database such as
# SQLite, MySQL, etc.
from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy object. This object contains functions and helpers to manipulate SQL databases using ORM
# techniques. It also handles session management for the user.
db = SQLAlchemy()

# Define the name of the database to be used with your Flask application.
# In this case, it's a SQLite database named 'database.db'.
DB_NAME = "database.db"

"""
The flask application package.
"""
import logging
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object(Config)
# Initialize Flask extensions
try:
    Session(app)
    db = SQLAlchemy(app)
    login = LoginManager(app)
    login.login_view = 'login'
# Test database connection
    with db.engine.connect() as connection:
        connection.execute('SELECT 1')
    logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise
import FlaskWebProject.views

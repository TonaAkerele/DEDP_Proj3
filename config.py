import os
from urllib.parse import quote_plus
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'm768Q~SV~bq_AEpWSA1MEyBuzyB5aZbk22gtSaxt'
# Blob Storage
    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'udacitystorage2'
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY') or 'ieVpYnh4Z6XnbtFEKqFTJWw3/15Ic4hg0mDSGu91FqMVyUxe1gKTfNrYgInu/mvo0SEKu/H3mClV+AStO5j0gA=='
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER') or 'images'
# SQL Database
    SQL_SERVER = os.environ.get('SQL_SERVER') or 'tonacms.database.windows.net'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'cms'
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or 'servercms'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or 'Udacitystudent@'
# Connection string with timeout and connection pooling
    params = quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};' +
        f'SERVER={SQL_SERVER};' +
        f'DATABASE={SQL_DATABASE};' +
        f'UID={SQL_USER_NAME};' +
        f'PWD={SQL_PASSWORD};' +
        'Connection Timeout=30;' +
        'Command Timeout=30;' +
        'Pooling=true;' +
        'Min Pool Size=5;' +
        'Max Pool Size=30'
    )
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# Microsoft Authentication
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or "goe8Q~ynpD_zoAEXA3feMphz4rNOo1H0zYqJdaif"
    AUTHORITY = "https://login.microsoftonline.com/common"
    CLIENT_ID = os.environ.get('CLIENT_ID') or "9e519a27-910a-4c10-bbc3-7d9de89ffcf9"
    REDIRECT_PATH = "/getAToken"
    HOMEPAGE = 'https://udacitycmstona-bpgvgkcpatfecton.canadacentral.azurewebsites.net'
    POST_LOGOUT_REDIRECT_URI = f"{HOMEPAGE}/login"
    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"

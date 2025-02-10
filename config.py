import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'm768Q~SV~bq_AEpWSA1MEyBuzyB5aZbk22gtSaxt'

    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'udacitystorage2'
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY') or 'ieVpYnh4Z6XnbtFEKqFTJWw3/15Ic4hg0mDSGu91FqMVyUxe1gKTfNrYgInu/mvo0SEKu/H3mClV+AStO5j0gA=='
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER') or 'images'

    SQL_SERVER = os.environ.get('SQL_SERVER') or 'tonacms.database.windows.net'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'cms'
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or 'servercms'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or 'Udacitystudent@'
    # Below URI may need some adjustments for driver version, based on your OS, if running locally
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://' + SQL_USER_NAME + '@' + SQL_SERVER + ':' + SQL_PASSWORD + '@' + SQL_SERVER + ':1433/' + SQL_DATABASE  + '?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Info for MS Authentication ###
    ### As adapted from: https://github.com/Azure-Samples/ms-identity-python-webapp ###
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or "goe8Q~ynpD_zoAEXA3feMphz4rNOo1H0zYqJdaif"
    # In your production app, Microsoft recommends you to use other ways to store your secret,
    # such as KeyVault, or environment variable as described in Flask's documentation here:
    # https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
    # CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    # if not CLIENT_SECRET:
    #     raise ValueError("Need to define CLIENT_SECRET environment variable")

    AUTHORITY = os.environ.get('AUTHORITY') or "https://login.microsoftonline.com/common"  # For multi-tenant app, else put tenant name
    # AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

    CLIENT_ID = os.environ.get('CLIENT_ID') or "9e519a27-910a-4c10-bbc3-7d9de89ffcf9"

    REDIRECT_PATH = os.environ.get('AUTHORITY') or "/getAToken"  # Used to form an absolute URL; must match to app's redirect_uri set in AAD
    POST_LOGOUT_REDIRECT_URI = "https://udacitycmstona-bpgvgkcpatfecton.canadacentral.azurewebsites.net/login"
    HOMEPAGE = 'https://udacitycmstona-bpgvgkcpatfecton.canadacentral.azurewebsites.net'
    
    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPE = ["User.Read"] # Only need to read user profile for this app

    SESSION_TYPE = "filesystem"  # Token cache will be stored in server-side session

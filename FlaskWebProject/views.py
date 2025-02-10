"""

Routes and views for the flask application.

"""

import logging

import uuid

from datetime import datetime

import msal

from flask import render_template, flash, redirect, request, session, url_for

from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlparse as url_parse

from werkzeug.utils import secure_filename

from azure.storage.blob import BlobClient
 
from FlaskWebProject import app, db

from FlaskWebProject.forms import LoginForm, PostForm

from FlaskWebProject.models import User, Post

from config import Config
 
# Configure logging

logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(levelname)s - %(message)s'

)

logger = logging.getLogger(__name__)
 
# Constants

TOKEN_CACHE = "token_cache"
 
# Azure Blob Storage URL for images

imageSourceUrl = f"https://{app.config['BLOB_ACCOUNT']}.blob.core.windows.net/{app.config['BLOB_CONTAINER']}"
 
@app.route('/')

@app.route('/home')

@login_required

def home():

    logger.info(f"User {current_user.username} accessed home page")

    posts = Post.query.all()

    return render_template(

        'index.html',

        title='Home Page',

        posts=posts

    )
 
@app.route('/post/<int:id>', methods=['GET', 'POST'])

@login_required

def post(id):

    logger.info(f"User {current_user.username} accessing post {id}")

    post = Post.query.get_or_404(id)

    form = PostForm(obj=post)

    if form.validate_on_submit():

        logger.info(f"User {current_user.username} updating post {id}")

        post.title = form.title.data

        post.body = form.body.data

        if form.image_path.data:

            try:

                filename = secure_filename(form.image_path.data.filename)

                logger.info(f"User {current_user.username} uploading image: {filename}")

                blob_client = BlobClient.from_connection_string(

                    app.config['BLOB_STORAGE_KEY'],

                    container_name=app.config['BLOB_CONTAINER'],

                    blob_name=filename

                )

                blob_client.upload_blob(form.image_path.data.read(), overwrite=True)

                post.image_path = filename

                logger.info(f"User {current_user.username} successfully uploaded image: {filename}")

            except Exception as e:

                logger.error(f"Error uploading image by user {current_user.username}: {str(e)}")

                flash(f"Error uploading image: {str(e)}")

        db.session.commit()

        logger.info(f"User {current_user.username} successfully updated post {id}")

        flash('Your post has been updated!')

        return redirect(url_for('home'))
 
    return render_template(

        'post.html',

        title='Edit Post',

        form=form,

        post=post,

        imageSource=imageSourceUrl,

        sas_token=app.config['BLOB_SAS_TOKEN']

    )
 
@app.route('/new_post', methods=['GET', 'POST'])

@login_required

def new_post():

    logger.info(f"User {current_user.username} accessing new post page")

    form = PostForm()

    if form.validate_on_submit():

        try:

            logger.info(f"User {current_user.username} creating new post")

            post = Post(

                title=form.title.data,

                body=form.body.data,

                author=form.author.data,

                user_id=current_user.id,

                timestamp=datetime.utcnow()

            )

            if form.image_path.data:

                try:

                    filename = secure_filename(form.image_path.data.filename)

                    logger.info(f"User {current_user.username} uploading image: {filename}")

                    blob_client = BlobClient.from_connection_string(

                        app.config['BLOB_STORAGE_KEY'],

                        container_name=app.config['BLOB_CONTAINER'],

                        blob_name=filename

                    )

                    blob_client.upload_blob(form.image_path.data.read(), overwrite=True)

                    post.image_path = filename

                    logger.info(f"User {current_user.username} successfully uploaded image: {filename}")

                except Exception as e:

                    logger.error(f"Error uploading image by user {current_user.username}: {str(e)}")

                    flash(f"Error uploading image: {str(e)}")

            db.session.add(post)

            db.session.commit()

            logger.info(f"User {current_user.username} successfully created new post")

            flash('Your post has been created!')

            return redirect(url_for('home'))

        except Exception as e:

            logger.error(f"Error creating post by user {current_user.username}: {str(e)}")

            db.session.rollback()

            flash(f"Error creating post: {str(e)}")

    return render_template(

        'post.html',

        title='Create Post',

        form=form,

        imageSource=imageSourceUrl

    )
 
@app.route('/login', methods=['GET', 'POST'])

def login():

    if current_user.is_authenticated:

        logger.info(f"Already authenticated user {current_user.username} accessing login page")

        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):

            logger.warning(f"Failed login attempt for username: {form.username.data}")

            flash('Invalid username or password')

            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        logger.info(f"Successful login for user: {user.username}")

        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':

            next_page = url_for('home')

        return redirect(next_page)

    session["state"] = str(uuid.uuid4())

    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])

    logger.info("User accessing login page")

    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)
 
@app.route(Config.REDIRECT_PATH)

def authorized():

    if request.args.get('state') != session.get("state"):

        logger.warning("State mismatch in authorized callback")

        return redirect(url_for("home"))

    if "error" in request.args:

        logger.error(f"Authorization error: {request.args.get('error')}")

        return render_template("auth_error.html", result=request.args)

    if request.args.get('code'):

        cache = _load_cache()

        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(

            request.args['code'],

            scopes=Config.SCOPE,

            redirect_uri=url_for('authorized', _external=True, _scheme='https'))

        if "error" in result:

            logger.error(f"Token acquisition error: {result.get('error')}")

            return render_template("auth_error.html", result=result)

        session["user"] = result.get("id_token_claims")

        user = User.query.filter_by(username=session["user"].get("preferred_username")).first()

        if not user:

            logger.info(f"Creating new user account for: {session['user'].get('preferred_username')}")

            user = User(username=session["user"].get("preferred_username"))

            user.set_password(str(uuid.uuid4()))

            db.session.add(user)

            db.session.commit()

        login_user(user)

        logger.info(f"Successful Microsoft login for user: {user.username}")

        _save_cache(cache)

    return redirect(url_for('home'))
 
@app.route('/logout')

def logout():

    if current_user.is_authenticated:

        username = current_user.username

        logger.info(f"User {username} logging out")

        logout_user()

        if session.get("user"):

            session.clear()

            logger.info(f"User {username} successfully logged out")

            return redirect(

                Config.AUTHORITY + "/oauth2/v2.0/logout" +

                "?post_logout_redirect_uri=" + url_for("login", _external=True))

    return redirect(url_for('login'))
 
def _load_cache():

    cache = msal.SerializableTokenCache()

    if session.get(TOKEN_CACHE):

        cache.deserialize(session[TOKEN_CACHE])

    return cache
 
def _save_cache(cache):

    if cache.has_state_changed:

        session[TOKEN_CACHE] = cache.serialize()
 
def _build_msal_app(cache=None, authority=None):

    return msal.ConfidentialClientApplication(

        Config.CLIENT_ID,

        authority=authority or Config.AUTHORITY,

        client_credential=Config.CLIENT_SECRET,

        token_cache=cache)
 
def _build_auth_url(authority=None, scopes=None, state=None):

    return _build_msal_app(authority=authority).get_authorization_request_url(

        scopes or [],

        state=state or str(uuid.uuid4()),

        redirect_uri=url_for('authorized', _external=True, _scheme='https'))
 


"""
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post
import msal
import uuid

imageSourceUrl = 'https://'+ app.config['BLOB_ACCOUNT']  + '.blob.core.windows.net/' + app.config['BLOB_CONTAINER']  + '/'

@app.route('/')
@app.route('/home')
@login_required
def home():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.all()
    return render_template(
        'index.html',
        title='Home Page',
        posts=posts
    )

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, request.files['image_path'], current_user.id, new=True)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Create Post',
        imageSource=imageSourceUrl,
        form=form
    )


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get(int(id))
    form = PostForm(formdata=request.form, obj=post)
    if form.validate_on_submit():
        post.save_changes(form, request.files['image_path'], current_user.id)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Edit Post',
        imageSource=imageSourceUrl,
        form=form
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)

@app.route(Config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("home"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        # TODO: Acquire a token from a built msal app, along with the appropriate redirect URI
        result = None
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        # Note: In a real app, we'd use the 'name' property from session["user"] below
        # Here, we'll use the admin username for anyone who is authenticated by MS
        user = User.query.filter_by(username="admin").first()
        login_user(user)
        _save_cache(cache)
    return redirect(url_for('home'))

@app.route('/logout')

'''
def logout():
    """Log out the user."""
    logout_user()
   
    if session.get("user"):  # If MS Login was used
        logger.info(f"User {session['user']['name']} logged out.")
        session.clear()  # Clear token cache and session data
       
        return redirect(
            Config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("login", _external=True)
        )
   
    return redirect(url_for('login'))
 
 
# MSAL helpers
def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get(TOKEN_CACHE):
        cache.deserialize(session[TOKEN_CACHE])
    return cache
 
 
def _save_cache(cache):
    if cache.has_state_changed:
        session[TOKEN_CACHE] = cache.serialize()
 
 
def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache
    )
 
 
def _build_auth_url(state=None):
    """Build the Microsoft Authentication URL."""
    return _build_msal_app().get_authorization_request_url(
        scopes=Config.SCOPE,
        state=state,
        redirect_uri=url_for('authorized', _external=True, _scheme='http')  # Use HTTP for local testing
    )
 

def logout():
    logout_user()
    if session.get("user"): # Used MS Login
        #Wipe out user and its token cache from session
        session.clear()
        # Also logout from your tenant's web session
        return redirect(
            Config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("login", _external=True))

    return redirect(url_for('login'))

def _load_cache():
    # TODO: Load the cache from `msal`, if it exists
    cache = None
    return cache

def _save_cache(cache):
     TODO: Save the cache, if it has changed
    pass

def _build_msal_app(cache=None, authority=None):
    # TODO: Return a ConfidentialClientApplication
    return None

def _build_auth_url(authority=None, scopes=None, state=None):
    TODO: Return the full Auth Request URL with appropriate Redirect URI
    return None

"""

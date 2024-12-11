from flask import Flask, request, redirect, url_for, render_template
from flask_mysqldb import MySQL
import os
import yaml
from flask import session
from flask import g  # For storing user info globally during the request            


mysql = MySQL()  # Make this a global variable



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']= '2kviuw40fg5mgd04n' # Thsis key secores the session Data

    # Get the path to the current directory and construct the path to db.yaml
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.yaml')


    # Load the database configuration
    db = yaml.load(open(db_path), Loader=yaml.FullLoader)

    app.config['SECRET_KEY'] = 'SECRET_KEY'
    # DATABASE configuration
    app.config['MYSQL_HOST'] = db['mysql_host']
    app.config['MYSQL_USER'] = db['mysql_user']
    app.config['MYSQL_PASSWORD'] = db['mysql_password']
    app.config['MYSQL_DB'] = db['mysql_db']

   
    mysql.init_app(app)


    # Import and register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .pushups import pushups as pushups_blueprint
    app.register_blueprint(pushups_blueprint)

    from .error import error as error_blueprint
    app.register_blueprint(error_blueprint)

    # Disable debug mode for production
    app.config['DEBUG'] = False  # This ensures debug mode is turned off


    # Apply the after_request function to set Cache-Control headers globally
    @app.after_request
    def add_header(response):
        # Prevent caching of pages
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    
    return app

    
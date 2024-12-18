"""
Application factory.
For details, see the Flask tutorial:
https://flask.palletsprojects.com/en/stable/tutorial/factory/

Github:
https://github.com/blep/flaskr

"""

import os
import logging

import boto3
from flask import Flask, render_template, send_from_directory
from . import db
from . import lab4_apikey
from . import lab4_image_controller

LOG_LEVEL = logging.DEBUG
USERNAME = 'simsong'

# Define the CORS configuration
CORS_CONFIGURATION = {
    'CORSRules': [
        {
            'AllowedOrigins': ['*'],               # Allow all origins with presigned POST and GETs
            'AllowedMethods': ['GET', 'POST', 'PUT'],     # Methods to allow
            'AllowedHeaders': ['*'],               # Allow all headers
            'MaxAgeSeconds': 3000                  # Cache duration for preflight requests
        }
    ]
}


def create_app(test_config=None):
    """create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)
    app.logger.setLevel(LOG_LEVEL)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'lab4.sqlite'),
        MAX_IMAGE_SIZE=10_000_000,
        S3_BUCKET=f'{USERNAME}-cscie-11-s3-bucket'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Apply the CORS policy to the S3 bucket
    s3 = boto3.client('s3')
    s3.put_bucket_cors(
        Bucket=app.config['S3_BUCKET'],
        CORSConfiguration=CORS_CONFIGURATION
    )


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Route templates
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('static', 'favicon.ico')

    @app.route('/about')
    def about():
        return render_template('about.html')

    db.init_app(app)
    lab4_image_controller.init_app(app)
    lab4_apikey.init_app(app)
    return app

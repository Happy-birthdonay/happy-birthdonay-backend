from datetime import datetime
from flask import Flask
from flask_cors import CORS

from app.models import db
from app.controllers import google_secret_controller

JWT_TOKEN_LOCATION = ['headers', 'cookies']
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=7)


def create_app(test_config=None):
    app = Flask(__name__)
    secret_controller = google_secret_controller.GoogleSecretController()
    DB_URL = secret_controller.access_secret('db_url')
    JWT_SECRET_KEY = secret_controller.access_secret('jwt_secret_key')

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JSON_AS_ASCII'] = False
    app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES

    # Database Setting
    db.init_app(app)

    # CORS Setting
    CORS(app, resources={r'*': {'origins': '*'}})
    return app

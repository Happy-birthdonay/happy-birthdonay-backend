from config import DB_URL, JWT_SECRET_KEY, JWT_TOKEN_LOCATION, JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES

from flask import Flask
from flask_cors import CORS

from app.models import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.debug = True
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

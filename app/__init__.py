from config import DB_URL

from flask import Flask
from flask_cors import CORS

from app.models import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

    # Database Setting
    db.init_app(app)

    # CORS Setting
    CORS(app, resources={r'*': {'origins': '*'}})
    return app

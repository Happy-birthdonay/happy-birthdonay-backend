from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.controllers import google_secret_controller


def get_secrets(secret_key_str):
    secret_controller = google_secret_controller.GoogleSecretController()
    return secret_controller.access_secret(secret_key_str)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_secrets('db_url')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}
db = SQLAlchemy(app)

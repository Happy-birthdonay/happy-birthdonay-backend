from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import DB_URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)


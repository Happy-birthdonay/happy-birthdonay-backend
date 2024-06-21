from flask import Blueprint

ping_app = Blueprint('oauth_app', __name__)

@ping_app.route('/ping')
def ping():
    print('ping pong test')
    return 'pong'

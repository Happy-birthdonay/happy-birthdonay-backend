from flask import logging
from flask_jwt_extended import JWTManager

from app import create_app
from app.routes.certifications import certifications_app
from app.routes.donation_boxes import donation_boxs_app
from app.routes.messages import messages_app
from app.routes.users import users_app
from app.routes.oauth import kakao_oauth_app
from app.routes.ping import ping_app

# Start of the App
app = create_app()
jwt = JWTManager(app)

app.register_blueprint(certifications_app)
app.register_blueprint(messages_app)
app.register_blueprint(donation_boxs_app)
app.register_blueprint(users_app)
app.register_blueprint(kakao_oauth_app)
app.register_blueprint(ping_app)

# Logger
logger = logging.create_logger(app)

# Run the App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

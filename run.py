from flask import request, jsonify, logging
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required
from datetime import datetime

from app import create_app, db

from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user

# Start of the App
app = create_app()
jwt = JWTManager(app)

logger = logging.create_logger(app)


# Routes
@app.route('/oauth/token', methods=['POST'])
def kakao_oauth():
    # Get the code from the request
    code = request.get_json()['code']

    # Authorize the code and get access token
    kakao_oauth_controller = KakaoOAuthController()
    authorization_infos = kakao_oauth_controller.authorization(code)

    if authorization_infos.get('access_token') is None:
        # TODO: - Make the response more specific
        return jsonify(result='failure',
                       message='Failed Kakao Login'), 401

    # Get user info using kakao access token
    access_token = authorization_infos['access_token']
    user_infos = kakao_oauth_controller.get_user_info(access_token)

    if user_infos is None:
        # TODO: - Make the response more specific
        return jsonify(result='failure',
                       message='Failed Kakao Login'), 401

    # Add the user to the database
    new_user = user.User(name=user_infos['kakao_account']['name'],
                         birthday=datetime.strptime(user_infos['kakao_account']['birthday'], '%m%d'))
    db.session.add(new_user)
    db.session.commit()
    db.session.refresh(new_user)

    # Make tokens and add them to the user
    new_user_dict = dict(new_user)
    new_user_token_data = {'name': new_user.name, 'birthday': new_user.birthday}
    new_access_token = create_access_token(identity=new_user_dict['user_id'], additional_claims=new_user_token_data)
    new_refresh_token = create_refresh_token(identity=new_user_dict['user_id'], additional_claims=new_user_token_data)

    new_user.access_token = new_access_token
    new_user.refresh_token = new_refresh_token
    db.session.commit()

    # Make the response
    res = jsonify(result='success',
                  message='Succeeded Kakao Login',
                  data=new_user_dict)

    # Set the cookies
    res.set_cookie('access_token', new_access_token)
    res.set_cookie('refresh_token', new_refresh_token)

    return res, 200


@app.route('/sign-up/{int:user_id}', methods=['PATCH'])
@jwt_required()
def sign_up(user_id):
    pass


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    pass


@app.route('/donation-boxes', methods=['POST'])
@jwt_required()
def create_donation_box():
    pass


@app.route('/donation-boxes', methods=['GET'])
@jwt_required()
def get_donation_boxes():
    pass


@app.route('/donation-boxes/<int:donation_box_id>', methods=['GET'])
@jwt_required()
def get_donation_box(donation_box_id):
    pass


@app.route('/donation-boxes/<int:donation_box_id>', methods=['PATCH'])
@jwt_required()
def update_donation_box(donation_box_id):
    pass


@app.route('/messages', methods=['POST'])
@jwt_required()
def create_message():
    pass


@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    pass


@app.route('/certifications', methods=['POST'])
@jwt_required()
def create_certification():
    pass


@app.route('/certifications/<int:donation_box_id>', methods=['GET'])
@jwt_required()
def get_certification(donation_box_id):
    pass


# Run the App
if __name__ == '__main__':
    app.run(debug=True, port=8000)

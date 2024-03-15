from flask import request, jsonify, logging
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required

from app import create_app, db

from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user

# Start of the App
app = create_app()
jwt = JWTManager(app)


# Routes

@app.route('/hello')
def index():
    return 'Hello, World!'

# MARK: - Kakao OAuth
# 1. Get the code from the request
# 2. Authorize the code and get access token from Kakao
# 3. Get user info using Kakao access token
# 4. Store user info in the database
# 5. Get user id from the database
# 6. Make our own tokens
# 7. Send and store the tokens to the client
@app.route('/oauth/token')
def kakao_oauth():
    # Get the code from the request
    code = request.get_json()['code']

    # Authorize the code and get access token
    kakao_oauth_controller = KakaoOAuthController()
    authorization_infos = kakao_oauth_controller.authorization(code)

    logger = logging.create_logger(app)
    logger.debug(authorization_infos.text)

    # Get user info using kakao access token
    access_token = authorization_infos.json()['access_token']
    user_infos = kakao_oauth_controller.get_user_info(access_token)

    if access_token is None or user_infos is None:
        # TODO: - Make the response more specific
        return jsonify(result='failure',
                       message='Failed Kakao Login'), 401
    else:
        # new_user = user.User(name=user_infos['kakao_account']['name'],
        #                      birthday=user_infos['kakao_account']['birthday'])
        new_user = user.User(name="eunbin",
                             birthday="0128")
        # MARK: - How to convert the string to datetime with format(YYYYMMDD)?
        new_user_id = 222

        # db.session.add(new_user)
        # db.session.commit()
        # MARK: - How to get the user id from the database?

        new_access_token = create_access_token(identity=new_user_id, additional_claims=new_user.to_json())
        new_refresh_token = create_refresh_token(identity=new_user_id, additional_claims=new_user.to_json())

        res = jsonify(result='success',
                      message='Succeeded Kakao Login',
                      data=new_user.to_json())

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
    app.run(debug=True)

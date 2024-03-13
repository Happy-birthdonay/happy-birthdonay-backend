from flask import request, jsonify, logging
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token

from app import create_app, db

from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user

# Start of the App
app = create_app()
jwt = JWTManager(app)


# Routes

@app.route('/oauth/token')
def kakao_oauth():
    # Get the code from the request
    code = request.get_json()['code']

    # Authorize the code and get access token
    kakao_oauth_controller = KakaoOAuthController()
    authorization_infos = kakao_oauth_controller.authorization(code)

    # logger = logging.create_logger(app)
    # logger.debug(authorization_infos.text)

    # Get user info using kakao access token
    access_token = authorization_infos.json()['access_token']
    user_infos = kakao_oauth_controller.get_user_info(access_token)

    if access_token is None or user_infos is None:
        # TODO: - Make the response more specific
        return jsonify(result='failure',
                       message='Failed Kakao Login'), 401
    else:
        # TODO: - 1. Store user info in the database
        # TODO: - 2. Get user id from the database
        # TODO: - 3. Make our own tokens

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


# Run the App
if __name__ == '__main__':
    app.run(debug=True)

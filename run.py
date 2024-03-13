from flask import request, jsonify, logging

from app import create_app

from app.controllers.kakao_oauth_controller import KakaoOAuthController

# Start of the App
app = create_app()


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
        return jsonify({
            'result': 'failure',
            'message': '카카오 로그인에 실패했습니다.'
        }), 401
    else:
        res = jsonify({
            'result': 'success',
            'message': '카카오 로그인에 성공했습니다.',
            'data': {
                'name': user_infos['kakao_account']['name'],
                'birthday': user_infos['kakao_account']['birthday'],
            }
        })

        # TODO: - Make our own access_token
        new_access_token = 'temporary_new_access_token'
        new_refresh_token = 'temporary_new_refresh_token'

        res.set_cookie('access_token', new_access_token)
        res.set_cookie('refresh_token', new_refresh_token)

        return res, 200


# Run the App
if __name__ == '__main__':
    app.run(debug=True)

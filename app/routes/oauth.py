from datetime import datetime

from flask import request, jsonify, Blueprint, json, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token

from app import db
from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user
from app.utilities.utility import camel_dict, json_serial_timestamp

kakao_oauth_app = Blueprint('kakao_oauth_app', __name__)


@kakao_oauth_app.route('/refresh')
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded Kakao Login: User already exists',
        'data': {
            'access_token': access_token
        }
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)
    res.set_cookie('access_token', access_token)

    return res, 200


@kakao_oauth_app.route('/oauth/token', methods=['POST'])
def kakao_oauth():
    # Get the code from the request
    code = request.get_json()['code']

    # Authorize the code and get access token
    kakao_oauth_controller = KakaoOAuthController()
    authorization_infos = kakao_oauth_controller.authorization(code)

    if authorization_infos.get('access_token') is None:
        # TODO: - Client should be notified about the failure and return to the kakao login page
        return jsonify(result='failure',
                       message='Failed Kakao Login: No access token. Check the kakao code again.'), 401

    # Get user info using kakao access token
    access_token = authorization_infos['access_token']
    user_infos = kakao_oauth_controller.get_user_info(access_token)

    if user_infos is None:
        return jsonify(result='failure',
                       message='Failed Kakao Login: No user information.'), 401

    # Query the user
    queried_user = user.User.query.filter_by(kakao_id=user_infos['id']).first()

    # If the user already exists, make the response and set the cookies
    if queried_user is not None:
        queried_user_dict = dict(queried_user)

        new_access_token = create_access_token(identity=queried_user_dict['user_id'],
                                               additional_claims={'kakao_id': queried_user_dict['kakao_id']})
        new_refresh_token = create_refresh_token(identity=queried_user_dict['user_id'],
                                                 additional_claims={'kakao_id': queried_user_dict['kakao_id']})

        result = json.dumps({
            'result': 'succeed',
            'message': 'Succeeded Kakao Login: User already exists',
            'data': camel_dict(queried_user_dict)
        }, ensure_ascii=False, indent=4, default=json_serial_timestamp)

        res = make_response(result)
        res.set_cookie('access_token', new_access_token)
        res.set_cookie('refresh_token', new_refresh_token)

        return res, 200

    # Add the new user to the database
    new_user = user.User(name=user_infos['kakao_account']['profile']['nickname'],
                         birthday=datetime.today().strftime('%m%d'),
                         kakao_id=user_infos['id'])
    # TODO: - If the db commit fails, the response should be failed
    db.session.add(new_user)
    db.session.commit()
    db.session.refresh(new_user)

    # Make tokens and add them to the user
    new_user_id = new_user.user_id
    new_access_token = create_access_token(identity=new_user_id,
                                           additional_claims={'kakao_id': user_infos['id']})
    new_refresh_token = create_refresh_token(identity=new_user_id,
                                             additional_claims={'kakao_id': user_infos['id']})

    new_user.access_token = new_access_token
    new_user.refresh_token = new_refresh_token

    # Make the response
    new_user_dict = dict(new_user)
    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded Kakao Login: New user added',
        'data': camel_dict(new_user_dict)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    # Set the cookies
    res.set_cookie('access_token', new_access_token)
    res.set_cookie('refresh_token', new_refresh_token)

    return res, 200

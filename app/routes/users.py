from flask import request, jsonify, Blueprint, json, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db

from app.models import user_model as user
from app.utilities.utility import camel_dict, json_serial_timestamp

users_app = Blueprint('users_app', __name__)


@users_app.route('/sign-up', methods=['PATCH'])
@jwt_required()
def sign_up():
    # Get the new data from the request
    new_data = request.get_json()

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    curr_user = user.User.query.filter_by(user_id=user_id).first()

    # Check if the new data is valid
    if new_data.get('name') is None or new_data.get('birthday') is None:
        return jsonify(result='failure',
                       message='Invalid Data: No name or birthday'), 400

    # Update the user
    if new_data['name'] != curr_user.name:
        curr_user.name = new_data['name']
    if new_data['birthday'] != curr_user.birthday:
        curr_user.birthday = new_data['birthday']

    # Commit the changes to the database and make the response data
    # TODO: - If the db commit fails, the response should be failed
    db.session.commit()
    changed_user_data = {
        'user_id': curr_user.user_id,
        'name': curr_user.name,
        'birthday': curr_user.birthday
    }

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded Sign up',
        'data': camel_dict(changed_user_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@users_app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    curr_user = user.User.query.filter_by(user_id=user_id).first()

    # Make the response data
    user_data = {
        'user_id': curr_user.user_id,
        'name': curr_user.name,
        'birthday': curr_user.birthday
    }
    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded Get user',
        'data': camel_dict(user_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@users_app.route('/users', methods=['PATCH'])
@jwt_required()
def edit_user_info():
    # Get the new data from the request
    new_data = request.get_json()

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    curr_user = user.User.query.filter_by(user_id=user_id).first()

    # Check if the new data is valid
    if new_data.get('name') is None or new_data.get('birthday') is None:
        return jsonify(result='failure',
                       message='Invalid Data: No name or birthday'), 400

    # Update the user
    if new_data['name'] != curr_user.name:
        curr_user.name = new_data['name']
    if new_data['birthday'] != curr_user.birthday:
        curr_user.birthday = new_data['birthday']

    # Commit the changes to the database and make the response data
    db.session.commit()
    changed_user_data = {
        'user_id': curr_user.user_id,
        'name': curr_user.name,
        'birthday': curr_user.birthday
    }

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded Sign up',
        'data': camel_dict(changed_user_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@users_app.route('/users', methods=['DELETE'])
@jwt_required()
def delete_user():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    curr_user = user.User.query.filter_by(user_id=user_id).first()

    if curr_user is None:
        return jsonify(result='failure',
                       message='No User found'), 404

    # Delete the user from the database
    db.session.delete(curr_user)
    db.session.commit()

    return jsonify(result='success',
                   message='Succeeded Delete user'), 200

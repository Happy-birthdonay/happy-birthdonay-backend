import json

from flask import request, jsonify, logging, make_response
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from app import create_app, db

from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user
from app.models import donation_box_model as donation_box
from app.models import message_model as message

from app.utilities.utility import camel_str, camel_dict, json_serial_timestamp

# Start of the App
app = create_app()
jwt = JWTManager(app)

# Logger
logger = logging.create_logger(app)


# Routes
@app.route('/refresh')
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


@app.route('/oauth/token', methods=['POST'])
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

        result = json.dumps({
            'result': 'succeed',
            'message': 'Succeeded Kakao Login: User already exists',
            'data': camel_dict(queried_user_dict)
        }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
        res = make_response(result)
        return res, 200

    # Add the new user to the database
    new_user = user.User(name=user_infos['kakao_account']['name'],
                         birthday=user_infos['kakao_account']['birthday'],
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


@app.route('/sign-up', methods=['PATCH'])
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
                       message='Invalid Data: No name or birthday'), 401

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


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    curr_user = user.User.query.filter_by(user_id=user_id).first()

    if curr_user is None:
        return jsonify(result='failure',
                       message='No User found'), 401

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


@app.route('/donation-boxes', methods=['POST'])
@jwt_required()
def create_donation_box():
    # Get the new data from the request
    new_data = request.get_json()

    # Get the user id from the token
    user_id = get_jwt_identity()
    new_donation_box = donation_box.DonationBox(user_id=user_id)

    # Check if the new data is valid
    for key in donation_box.BOX_VALUES:
        if new_data.get(camel_str(key)) is None:
            return jsonify(result='failure',
                           message=f'Invalid Data: No {camel_str(key)}'), 401
        else:
            setattr(new_donation_box, key, new_data[camel_str(key)])

    # Add the new donation box to the database
    db.session.add(new_donation_box)
    db.session.commit()
    db.session.refresh(new_donation_box)

    # TODO: - If the db commit fails, the response should be failed
    # Make the response data
    res_data = {
        'box_id': new_donation_box.box_id,
    }

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to create donation box',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@app.route('/donation-boxes', methods=['GET'])
@jwt_required()
def get_donation_boxes():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the donation boxes
    donation_boxes = donation_box.DonationBox.query.filter_by(user_id=user_id).all()

    if donation_boxes is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 401

    # Make the response data
    res_data = [camel_dict({
        'box_id': box.box_id,
        'color': box.color,
    }) for box in donation_boxes]

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation boxes',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@app.route('/donation-boxes/<int:donation_box_id>/guest', methods=['GET'])
def get_donation_box_for_guest(donation_box_id):
    queried_donation_box = donation_box.DonationBox.query.filter_by(box_id=donation_box_id).first()
    queried_messages_count = message.Message.query.filter_by(box_id=donation_box_id).count()

    if queried_donation_box is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 403

    res_data = dict(queried_donation_box)
    res_data.update({'message_count': queried_messages_count})

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation box',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@app.route('/donation-boxes/<int:donation_box_id>', methods=['GET'])
@jwt_required()
def get_donation_box(donation_box_id):
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the donation box
    queried_donation_box = donation_box.DonationBox.query.filter_by(box_id=donation_box_id, user_id=user_id).first()
    open_date_str = user.User.query.filter_by(user_id=user_id).first().birthday
    queried_messages = message.Message.query.filter_by(box_id=donation_box_id).count()

    if queried_donation_box is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 403

    # Make the response data
    res_data = dict(queried_donation_box)
    res_data.update({'open_date': f'{datetime.now().year}{open_date_str}'})
    res_data.update({'message_count': queried_messages})

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation box',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@app.route('/donation-boxes/<int:donation_box_id>', methods=['PATCH'])
@jwt_required()
def update_donation_box(donation_box_id):
    # Get the new data from the request
    new_data = request.get_json()

    if new_data.get('isDonated') is None:
        return jsonify(result='failure',
                       message='Invalid Data: No isDonated variable'), 401

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the donation box
    queried_donation_box = donation_box.DonationBox.query.filter_by(box_id=donation_box_id, user_id=user_id).first()

    if queried_donation_box is None:
        return jsonify(result='failure',
                       message=f'No Donation Box found: id {donation_box_id}'), 401

    # Commit the changes to the database and make the response data
    queried_donation_box.is_donated = new_data['is_donated']
    db.session.commit()

    return jsonify(result='success',
                   message='Succeeded Update Donation Box'), 200


@app.route('/messages', methods=['POST'])
def create_message():
    # Get the new data from the request
    new_data = request.get_json()
    new_message = message.Message()

    for key in message.MESSAGE_VALUES:
        if new_data.get(camel_str(key)) is None:
            return jsonify(result='failure',
                           message=f'Invalid Data: No {camel_str(key)}'), 401
        else:
            setattr(new_message, key, new_data[camel_str(key)])

    db.session.add(new_message)
    db.session.commit()

    # TODO: - If the db commit fails, the response should be failed
    return jsonify(result='success',
                   message='Succeeded Create Message'), 200


@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    # Get the data from the request
    box_id = request.args.get('boxId', type=int)

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Check if the box_id is valid
    if box_id is None:
        return jsonify(result='failure',
                       message='Invalid Data: No boxId'), 401

    # Check if the box_id is matched with the user_id
    if box_id is not None:
        curr_box = donation_box.DonationBox.query.filter_by(box_id=box_id).first()
        if curr_box.user_id != user_id:
            return jsonify(result='failure',
                           message='Invalid Data: BoxId and userId are not matched'), 401

    # Query the messages
    queried_messages = message.Message.query.filter_by(box_id=box_id).all()

    # Make the response data
    res_data = [camel_dict(dict(msg)) for msg in queried_messages]

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get messages',
        'data': res_data
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


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
    app.run(debug=True, host='127.0.0.1', port=8000)

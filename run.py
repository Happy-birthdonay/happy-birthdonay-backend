from flask import request, jsonify, logging
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime

from app import create_app, db

from app.controllers.kakao_oauth_controller import KakaoOAuthController

from app.models import user_model as user
from app.models import donation_box_model as donation_box
from app.models import message_model as message

from app.utilities.utility import camel_str, camel_dict

# Start of the App
app = create_app()
jwt = JWTManager(app)

# Logger
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
        return jsonify(result='failure',
                       message='Failed Kakao Login: No access token'), 401

    # Get user info using kakao access token
    access_token = authorization_infos['access_token']
    user_infos = kakao_oauth_controller.get_user_info(access_token)

    if user_infos is None:
        return jsonify(result='failure',
                       message='Failed Kakao Login: No user information'), 401

    # Query the user
    queried_user = user.User.query.filter_by(kakao_id=user_infos['id']).first()

    # If the user already exists, make the response and set the cookies
    if queried_user is not None:
        res = jsonify(result='succeed',
                      message='Succeeded Kakao Login: User already exists',
                      data=dict(queried_user))

        # TODO: - Is access token and refresh token should be updated?
        res.set_cookie('access_token', queried_user.access_token)
        res.set_cookie('refresh_token', queried_user.refresh_token)
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
    new_user_dict = camel_dict(dict(new_user))
    new_access_token = create_access_token(identity=new_user['user_id'], additional_claims=new_user_dict)
    new_refresh_token = create_refresh_token(identity=new_user['user_id'], additional_claims=new_user_dict)

    # TODO: - If the db commit fails, the response should be failed
    new_user.access_token = new_access_token
    new_user.refresh_token = new_refresh_token
    db.session.commit()

    # Make the response
    res = jsonify(result='success',
                  message='Succeeded Kakao Login: New user added',
                  data=new_user_dict)

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
    current_user = user.User.query.filter_by(user_id=user_id).first()

    # Check if the new data is valid
    if new_data.get('name') is None or new_data.get('birthday') is None:
        return jsonify(result='failure',
                       message='Invalid Data: No name or birthday'), 401

    # Update the user
    if new_data['name'] != current_user.name:
        current_user.name = new_data['name']
    if new_data['birthday'] != current_user.birthday:
        current_user.birthday = new_data['birthday']

    # Commit the changes to the database and make the response data
    # TODO: - If the db commit fails, the response should be failed
    db.session.commit()
    changed_user_data = {
        'user_id': current_user.user_id,
        'name': current_user.name,
        'birthday': current_user.birthday
    }

    return jsonify(result='success',
                   message='Succeeded Sign Up',
                   data=camel_dict(changed_user_data)), 200


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the user
    current_user = user.User.query.filter_by(user_id=user_id).first()

    if current_user is None:
        return jsonify(result='failure',
                       message='No User found'), 401

    # Make the response data
    user_data = {
        'user_id': current_user.user_id,
        'name': current_user.name,
        'birthday': current_user.birthday
    }
    return jsonify(result='success',
                   message='Succeeded Get User',
                   data=camel_dict(user_data)), 200


@app.route('/donation-boxes', methods=['POST'])
@jwt_required()
def create_donation_box():
    # Get the new data from the request
    new_data = request.get_json()

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Check if the new data is valid
    for key in donation_box.BOX_VALUES:
        if new_data.get(camel_str(key)) is None:
            return jsonify(result='failure',
                           message=f'Invalid Data: No {camel_str(key)}'), 401

    # Add the new donation box to the database
    new_donation_box = donation_box.DonationBox(name=new_data['name'],
                                                url=new_data['url'],
                                                title=new_data['box_title'],
                                                description=new_data['box_description'],
                                                amount=new_data['amount'],
                                                color=new_data['color'],
                                                user_id=user_id)
    db.session.add(new_donation_box)
    db.session.commit()
    db.session.refresh(new_donation_box)

    # TODO: - If the db commit fails, the response should be failed
    # Make the response data
    res_data = {
        'box_id': new_donation_box.box_id,
    }

    return jsonify(result='success',
                   message='Succeeded Create Donation Box',
                   data=camel_dict(res_data)), 200


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

    return jsonify(result='success',
                   message='Succeeded Get Donation Boxes',
                   data=res_data), 200


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
                       message='No Donation Box found'), 401

    # Make the response data
    res_data = dict(queried_donation_box)
    res_data.update({'open_date': f'{datetime.date.today().year}{open_date_str}'})
    res_data.update({'message_count': queried_messages})

    return jsonify(result='success',
                   message='Succeeded Get Donation Box',
                   data=camel_dict(res_data)), 200


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

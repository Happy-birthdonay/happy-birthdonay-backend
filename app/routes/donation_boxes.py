from datetime import datetime

from flask import request, jsonify, Blueprint, json, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db

from app.models import donation_box_model as donation_box
from app.models import message_model as message
from app.models import user_model as user
from app.utilities.utility import camel_dict, json_serial_timestamp, camel_str

donation_boxs_app = Blueprint('donation_boxs_app', __name__)


@donation_boxs_app.route('/donation-boxes', methods=['POST'])
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
                           message=f'Invalid Data: No {camel_str(key)}'), 400
        else:
            setattr(new_donation_box, key, new_data[camel_str(key)])

    # Add the new donation box to the database
    db.session.add(new_donation_box)
    db.session.commit()
    db.session.refresh(new_donation_box)

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


@donation_boxs_app.route('/donation-boxes', methods=['GET'])
@jwt_required()
def get_donation_boxes():
    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the donation boxes
    donation_boxes = donation_box.DonationBox.query.filter_by(user_id=user_id).all()

    if donation_boxes is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 404

    # Make the response data
    res_data = [camel_dict({
        'box_id': box.box_id,
        'color': box.color,
    }) for box in donation_boxes]

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation boxes',
        'data': res_data
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@donation_boxs_app.route('/donation-boxes/<int:donation_box_id>/guest', methods=['GET'])
def get_donation_box_for_guest(donation_box_id):
    queried_donation_box = donation_box.DonationBox.query.filter_by(box_id=donation_box_id).first()
    queried_messages_count = message.Message.query.filter_by(box_id=donation_box_id).count()

    if queried_donation_box is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 404

    user_name = user.User.query.filter_by(user_id=queried_donation_box.user_id).first().name
    res_data = dict(queried_donation_box)
    res_data.update({'created_by': user_name})
    res_data.update({'message_count': queried_messages_count})

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation box',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@donation_boxs_app.route('/donation-boxes/<int:donation_box_id>', methods=['GET'])
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
                       message='No Donation Box found'), 404

    # Need to update: - compare times between today and the open date(birthday, created_at)
    today_str = datetime.today().strftime('%m%d')
    open_date_year = datetime.today().year
    if open_date_str is today_str:
        open_date_str = str(int(open_date_str) + 1)
    elif open_date_str < today_str:
        if queried_donation_box.isDonated is False:
            open_date_year += 1

    # Make the response data
    res_data = dict(queried_donation_box)
    res_data.update({'open_date': f'{open_date_year}{open_date_str}'})
    res_data.update({'message_count': queried_messages})

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get donation box',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)
    res = make_response(result)

    return res, 200


@donation_boxs_app.route('/donation-boxes/<int:donation_box_id>', methods=['PATCH'])
@jwt_required()
def update_donation_box(donation_box_id):
    # Get the new data from the request
    new_data = request.get_json()

    if new_data.get('isDonated') is None:
        return jsonify(result='failure',
                       message='Invalid Data: No isDonated variable'), 404

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Query the donation box
    queried_donation_box = donation_box.DonationBox.query.filter_by(box_id=donation_box_id, user_id=user_id).first()

    if queried_donation_box is None:
        return jsonify(result='failure',
                       message=f'No Donation Box found: id {donation_box_id}'), 404

    # Commit the changes to the database and make the response data
    queried_donation_box.is_donated = new_data['isDonated']
    db.session.commit()

    return jsonify(result='success',
                   message='Succeeded Update Donation Box'), 200

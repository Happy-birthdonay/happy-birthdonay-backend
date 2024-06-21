from flask import request, jsonify, Blueprint, json, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db

from app.models import donation_box_model as donation_box
from app.models import message_model as message
from app.utilities.utility import camel_dict, json_serial_timestamp, camel_str

messages_app = Blueprint('messages_app', __name__)


@messages_app.route('/messages', methods=['POST'])
def create_message():
    # Get the new data from the request
    new_data = request.get_json()
    new_message = message.Message()

    for key in message.MESSAGE_VALUES:
        if new_data.get(camel_str(key)) is None:
            return jsonify(result='failure',
                           message=f'Invalid Data: No {camel_str(key)}'), 400
        else:
            setattr(new_message, key, new_data[camel_str(key)])

    db.session.add(new_message)
    db.session.commit()

    # TODO: - If the db commit fails, the response should be failed
    return jsonify(result='success',
                   message='Succeeded Create Message'), 200


@messages_app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    # Get the data from the request
    box_id = request.args.get('boxId', type=int)

    # Get the user id from the token
    user_id = get_jwt_identity()

    # Check if the box_id is valid
    if box_id is None:
        return jsonify(result='failure',
                       message='Invalid Data: No boxId'), 404

    # Check if the box_id is matched with the user_id
    curr_box = donation_box.DonationBox.query.filter_by(user_id=user_id, box_id=box_id).first()

    if curr_box is None:
        return jsonify(result='failure',
                       message='Invalid Data: BoxId and userId are not matched'), 404

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

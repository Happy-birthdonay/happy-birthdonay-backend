from datetime import datetime

from flask import request, jsonify, Blueprint, json, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.controllers.s3_controller import S3Controller

from app.models import donation_box_model as donation_box
from app.models import user_model as user
from app.models import message_model as message
from app.utilities.utility import camel_dict, json_serial_timestamp

certifications_app = Blueprint('certifications_app', __name__)


@certifications_app.route('/certifications/<int:donation_box_id>', methods=['POST'])
@jwt_required()
def save_certification_image(donation_box_id):
    new_data = request.files['imageData']

    s3_client = S3Controller()
    s3_client.put_object(f'{donation_box_id}.png', new_data)
    image_url = s3_client.get_image_url(f'{donation_box_id}.png')

    user_id = get_jwt_identity()

    queried_box = donation_box.DonationBox.query.filter_by(user_id=user_id, box_id=donation_box_id).first()

    queried_box.cert_img_url = image_url
    queried_box.cert_created_at = datetime.now().strftime('%Y-%m-%d')

    db.session.commit()

    return jsonify(result='success',
                   message='Succeeded to save certification image'), 200


@certifications_app.route('/certifications/<int:donation_box_id>', methods=['GET'])
@jwt_required()
def get_certification_image(donation_box_id):
    user_id = get_jwt_identity()
    queried_box = donation_box.DonationBox.query.filter_by(user_id=user_id, box_id=donation_box_id).first()

    if queried_box is None:
        return jsonify(result='failure',
                       message='No Donation Box found'), 404

    user_data = user.User.query.filter_by(user_id=user_id).first()

    if user_data is None or user_data.name is None:
        return jsonify(result='failure',
                       message='No User found'), 404

    message_data = message.Message.query.filter_by(box_id=donation_box_id).all()
    donors_name_list = []

    if message_data is not []:
        for msg in message_data:
            donors_name_list.append(msg.created_by)

    res_data = {
        'box_id': queried_box.box_id,
        'name': queried_box.name,
        'box_created_by': user_data.name,
        'donors_name_list': donors_name_list,
        'cert_img_url': queried_box.cert_img_url,
        'cert_created_at': queried_box.cert_created_at
    }

    result = json.dumps({
        'result': 'succeed',
        'message': 'Succeeded to get certification image',
        'data': camel_dict(res_data)
    }, ensure_ascii=False, indent=4, default=json_serial_timestamp)

    res = make_response(result)
    return res, 200

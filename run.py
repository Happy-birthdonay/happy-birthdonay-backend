from app import create_app
from app.models.user_model import User
from app.models.donation_box_model import DonationBox

# Start of the App
app = create_app()


# Routes
@app.route('/hw')
def hello_world():
    return 'Hello, World!'


@app.route('/users')
def get_all_users():
    users = User.query.all()
    return {
        'user_id': [user.user_id for user in users],
        'name': [user.name for user in users],
        'birthday': [user.birthday for user in users],
        'access_token': [user.access_token for user in users],
        'refresh_token': [user.refresh_token for user in users]
    }


@app.route('/donation-boxes/<int:box_id>')
def get_donation_box(box_id):
    boxInfo = DonationBox.query.filter_by(id=box_id).first()
    return {
        'box_id': boxInfo.id,
        'name': boxInfo.name,
        'description': boxInfo.description,
        'user_id': boxInfo.user_id,
    }


# Run the App
if __name__ == '__main__':
    app.run(debug=True)

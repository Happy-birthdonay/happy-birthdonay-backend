import datetime
from app.models import db

KST = datetime.timezone(datetime.timedelta(hours=9))


class User(db.Model):
    """
    User Model
    - user_id: 사용자 아이디, INT, PK
    - name: 사용자 이름, VARCHAR(50)
    - birthday: 사용자 생일, DATETIME
    - access_token: 사용자 토큰, VARCHAR(250)
    - refresh_token: 사용자 리프레시 토큰, VARCHAR(250)
    - updated_at: 업데이트 시간, DATETIME
    """

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False, default=KST)
    access_token = db.Column(db.String(250), nullable=False)
    refresh_token = db.Column(db.String(250), nullable=False)
    updated_at = db.Column(db.DateTime, default=KST, onupdate=KST)

    def __init__(self, name, birthday, access_token, refresh_token):
        self.name = name
        self.birthday = birthday
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.updated_at = datetime.datetime.now()

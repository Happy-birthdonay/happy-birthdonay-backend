import datetime
from app.models import db

# KST = datetime.timezone(datetime.timedelta(hours=9))


class User(db.Model):
    """
    User Model
    - user_id: 사용자 아이디, INT, PK
    - name: 사용자 이름, VARCHAR(50)
    - birthday: 사용자 생일, VARCHAR(6)
    - kakao_id: 카카오 아이디, INT
    - access_token: 사용자 토큰, VARCHAR(250)
    - refresh_token: 사용자 리프레시 토큰, VARCHAR(250)
    - updated_at: 업데이트 시간, DATETIME
    """

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.String(6), nullable=False)
    kakao_id = db.Column(db.Integer, nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, birthday, kakao_id):
        self.name = name
        self.birthday = birthday
        self.kakao_id = kakao_id
        # self.updated_at = datetime.datetime.now()
        self.access_token = ''
        self.refresh_token = ''

    def __iter__(self):
        yield 'user_id', self.user_id
        yield 'name', self.name
        yield 'birthday', self.birthday
        yield 'kakao_id', self.kakao_id
        yield 'access_token', self.access_token
        yield 'refresh_token', self.refresh_token
        yield 'updated_at', self.updated_at

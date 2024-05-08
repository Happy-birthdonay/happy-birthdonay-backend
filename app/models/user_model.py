import datetime
from app.models import db

# KST = datetime.timezone(datetime.timedelta(hours=9))


class User(db.Model):
    """
    User Model
    - user_id: 사용자 아이디, INT, PK
    - name: 사용자 이름, VARCHAR(50)
    - birthday: 사용자 생일, VARCHAR(6)
    - kakao_id: 카카오 아이디, VARCHAR(20)
    - updated_at: 업데이트 시간, DATETIME
    """

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.String(6), nullable=False)
    kakao_id = db.Column(db.String(20), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, birthday, kakao_id):
        self.name = name
        self.birthday = birthday
        self.kakao_id = kakao_id
        self.updated_at = datetime.datetime.now()

    def __iter__(self):
        yield 'user_id', self.user_id
        yield 'name', self.name
        yield 'birthday', self.birthday
        yield 'kakao_id', self.kakao_id
        yield 'updated_at', self.updated_at

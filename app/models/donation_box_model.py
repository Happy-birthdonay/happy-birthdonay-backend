import datetime
from app.models import db

KST = datetime.timezone(datetime.timedelta(hours=9))

BOX_VALUES = ['name', 'url', 'box_title', 'box_description', 'amount', 'color']


class DonationBox(db.Model):
    """
    DonationBox Model
    - box_id: 상자 아이디, INT, PK
    - name: 기부처 이름, VARCHAR(100)
    - url: 상자 URL, VARCHAR(500)
    - box_title: 상자 이름, VARCHAR(100)
    - box_description: 상자 설명, VARCHAR(500)
    - amount: 상자 금액, INT
    - color: 상자 색상, VARCHAR(45)
    - is_donated: 상자 기부 여부, BOOLEAN
    - cert_img_url: 상자 인증 이미지 URL, VARCHAR(500)
    - cert_created_at: 상자 인증 시간, DATETIME
    - user_id: 사용자 아이디, INT, FK
    - updated_at: 업데이트 시간, DATETIME
    """

    __tablename__ = 'donation_box'

    box_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    box_title = db.Column(db.String(100), nullable=False)
    box_description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(45), nullable=False)
    is_donated = db.Column(db.Boolean, nullable=False, default=False)
    cert_img_url = db.Column(db.String(250), nullable=True)
    cert_created_at = db.Column(db.DateTime, nullable=True, default=KST)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=KST, onupdate=KST)

    # def __init__(self, name, url, title, description, amount, color, user_id):
    #     self.name = name
    #     self.url = url
    #     self.box_title = title
    #     self.box_description = description
    #     self.amount = amount
    #     self.color = color
    #     self.user_id = user_id
    #     self.updated_at = datetime.datetime.now()

    def __init__(self, user_id):
        self.name = ''
        self.url = ''
        self.box_title = ''
        self.box_description = ''
        self.amount = 0
        self.color = ''
        self.user_id = user_id
        self.updated_at = datetime.datetime.now()

    def __iter__(self):
        yield 'box_id', self.box_id
        yield 'name', self.name
        yield 'url', self.url
        yield 'box_title', self.box_title
        yield 'box_description', self.box_description
        yield 'amount', self.amount
        yield 'color', self.color
        yield 'is_donated', self.is_donated
        yield 'cert_img_url', self.cert_img_url
        yield 'cert_created_at', self.cert_created_at
        yield 'user_id', self.user_id
        yield 'updated_at', self.updated_at

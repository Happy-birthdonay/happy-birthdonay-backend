import datetime
from app.models import db

KST = datetime.timezone(datetime.timedelta(hours=9))

MESSAGE_VALUES = ['box_id', 'created_by', 'tag', 'contents']


class Message(db.Model):
    """
    Message Model
    - message_id: 메시지 아이디, INT, PK
    - box_id: 박스 아이디, INT, FK
    - created_by: 메시지 보낸 사람, VARCHAR(20)
    - tag: 태그 - 메시지 테마, VARCHAR(45)
    - content: 메시지 내용, VARCHAR(600)
    - created_at: 메시지 생성 시간, DATETIME
    """

    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('donation_box.id'), nullable=False)
    created_by = db.Column(db.String(20), nullable=False)
    tag = db.Column(db.String(45), nullable=False)
    content = db.Column(db.String(600), nullable=False)
    created_at = db.Column(db.DateTime, default=KST)

    # def __init__(self, box_id, created_by, tag, content):
    #     self.box_id = box_id
    #     self.created_by = created_by
    #     self.tag = tag
    #     self.content = content
    #     self.created_at = datetime.datetime.now()

    def __init__(self, **kwargs):
        for key in MESSAGE_VALUES:
            if key in kwargs:
                setattr(self, key, kwargs[key])
        self.created_at = datetime.datetime.now()

    def __iter__(self):
        yield 'message_id', self.message_id
        yield 'box_id', self.box_id
        yield 'created_by', self.created_by
        yield 'tag', self.tag
        yield 'content', self.content
        yield 'created_at', self.created_at
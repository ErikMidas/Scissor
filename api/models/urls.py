import string
from datetime import datetime
from random import choices


from ..utils import db 

class Url(db.Model):
    __tablename__ = "urls"
    id = db.Column(db.Integer(), primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_url = db.Column(db.String(100), nullable=False, unique=True)
    url_code = db.Column(db.String(64), nullable=False)
    qr_code = db.Column(db.String(64), nullable=True)
    clicks = db.Column(db.Integer(), default=0)
    date_created = db.Column(db.DateTime(), default=datetime.now)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_link()

    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=6))

        link = self.query.filter_by(short_url=short_url).first()

        if link:
            return self.generate_short_link()
        
        return short_url
from . import bcrypt, db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    links = db.relationship("Link", backref="user", lazy=True)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()

    def __repr__(self):
        return f"User: <{self.username}>"
    

class Link(db.Model):
    
    __tablename__ = "links"
    
    id = db.Column(db.Integer, primary_key=True)
    long_link = db.Column(db.String())
    short_link = db.Column(db.String(10), unique=True)
    custom_link = db.Column(db.String(50), unique=True, default=None)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"Link: <{self.short_link}>"
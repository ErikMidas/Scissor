from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scissor.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300


bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app)
limiter = Limiter(get_remote_address)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

from .models import User
from . import routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()
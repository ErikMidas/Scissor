from flask import Flask
from flask_restx import Api
from .auth.views import auth_namespace
from .url.views import url_namespace
from .config.config import config_dict
from .utils import db
from .models.urls import Url
from .models.users import User
from flask_migrate import Migrate


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    
    app.config.from_object(config)
    
    db.init_app(app)

    migrate = Migrate(app, db)
    
    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; token to authorize **"
        }
    }
    
    api = Api(
        app,
        title="Scissor URL Shortener",
        description="A URL Shortener using REST API",
        version=1.0,
        authorizations=authorizations,
        security="Bearer Auth",
        contact_email="koats14@gmail.com"
        )

    api.add_namespace(auth_namespace)
    api.add_namespace(url_namespace)
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
            "Url":  Url
        }
        
    return app
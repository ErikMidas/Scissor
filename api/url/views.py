from flask import request
from flask_restx import Namespace, Resource, fields
# from ..models.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

url_namespace = Namespace("url", description="Namespace for URLs")
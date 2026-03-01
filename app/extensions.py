from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask import request

database = SQLAlchemy()
jwt = JWTManager()
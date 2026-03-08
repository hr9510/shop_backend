from flask import Flask, request, jsonify, Blueprint, Response
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token , create_refresh_token, set_access_cookies, set_refresh_cookies, jwt_required, get_jwt, get_jwt_identity

database = SQLAlchemy()
jwt = JWTManager()

def createApp():
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI" : "sqlite:///sql.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS" : False,
        "JWT_SECRET_KEY": "super_secret_key",
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=2),
        "JWT_REFRESH_TOKEN_EXPIRES": timedelta(days=30),
        "JWT_TOKEN_LOCATION" : ["cookies"],
        "JWT_COOKIE_SECURE" : True,
        "JWT_COOKIE_SAMESITE" : "Lax",
        "JWT_COOKIE_CSRF_PROTECT" : True,
    })
    database.init_app(app)
    jwt.init_app(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
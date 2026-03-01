from flask import Flask
from .extensions import database, jwt
from .routes import main_bp
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

def createApp():
    app = Flask(__name__)

    # DATABASE
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # COOKIE (CRITICAL FOR NEXTJS)
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "None"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    database.init_app(app)
    jwt.init_app(app)
    # limiter.init_app(app)

    app.register_blueprint(main_bp)

    return app
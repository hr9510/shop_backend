from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def createApp():
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI" : "sqlite:///sql.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS" : False
    })
    db.init_app(app)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
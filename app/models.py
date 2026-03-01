from datetime import datetime, date
from .extensions import database
from werkzeug.security import generate_password_hash, check_password_hash

class Users(database.Model):
    __tablename__ = "user_data"

    id = database.Column(database.Integer, primary_key=True)
    user_code = database.Column(database.String(8), unique=True, nullable=False)
    user_name = database.Column(database.String(30), nullable=False)
    user_email = database.Column(database.String(40), unique=True, nullable=False)
    password = database.Column(database.String(255), nullable=False)

    def encrypt_password(self, password):
        self.password = generate_password_hash(password)

    def check_encrypted_password(self, password):
        return check_password_hash(self.password, password)

class Products(database.Model):
    __tablename__ = "product_data"

    id = database.Column(database.Integer, primary_key=True)
    user_code = database.Column(database.String(8), database.ForeignKey("user_data.user_code"), nullable=False)

    name = database.Column(database.String(30), nullable=False)
    brand = database.Column(database.String(30))
    ram = database.Column(database.Integer)
    storage = database.Column(database.Integer)
    category = database.Column(database.String(30), nullable=False)
    status = database.Column(database.String(20), default="active", nullable=False)
    quantity = database.Column(database.Integer, default=0, nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)

class Purchase(database.Model):
    __tablename__ = "purchase_data"

    id = database.Column(database.Integer, primary_key=True)
    user_code = database.Column(database.String(8), database.ForeignKey("user_data.user_code"), nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("product_data.id"), nullable=False)

    quantity = database.Column(database.Integer, nullable=False)
    purchase_price = database.Column(database.Integer, nullable=False)
    supplier_name = database.Column(database.String(30))
    purchase_date = database.Column(database.Date, default=date.today)

class Sales(database.Model):
    __tablename__ = "sales_data"

    id = database.Column(database.Integer, primary_key=True)
    user_code = database.Column(database.String(8), database.ForeignKey("user_data.user_code"), nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("product_data.id"), nullable=False)

    quantity = database.Column(database.Integer, nullable=False)
    selling_price = database.Column(database.Integer, nullable=False)
    purchase_price = database.Column(database.Integer, nullable=False)
    selling_date = database.Column(database.Date, default=date.today)

class OtherManages(database.Model):
    __tablename__ = "other_data"

    id = database.Column(database.Integer, primary_key=True)
    user_code = database.Column(database.String(8), database.ForeignKey("user_data.user_code"), nullable=False)

    title = database.Column(database.String(100), nullable=False)
    note = database.Column(database.String(200))
    amount = database.Column(database.Integer, nullable=False)
    which_type = database.Column(database.String(30), nullable=False)
    date = database.Column(database.Date, default=date.today)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
from . import database, datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

class Shops(database.Model):
    __tablename__ = "Shops_Data"
    id = database.Column(database.Integer, primary_key=True)
    shop_name = database.Column(database.String(50), nullable=False)
    owner_name = database.Column(database.String(30), nullable=False)
    owner_contact = database.Column(database.Integer, unique=True, nullable=False)
    shop_address = database.Column(database.String(100), nullable=False)
    shop_code = database.Column(database.String(8), nullable=False, unique=True)
    created_at = database.Column(database.DateTime, default = datetime.utcnow)

class Users(database.Model):
    __tablename__ = "Users_Data"
    id = database.Column(database.Integer, primary_key = True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"), nullable=False)
    user_name = database.Column(database.String(30), nullable=False)
    email = database.Column(database.String(50),unique=True, nullable=False)
    password = database.Column(database.String(200), nullable=False)

    def encryptPassword(self, password):
        self.password = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)
    
class Products(database.Model):
    __tablename__ = "Products_Data"
    id = database.Column(database.Integer, primary_key = True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"), nullable=False)
    name = database.Column(database.String(50), nullable = False)
    brand = database.Column(database.String(50), nullable=False)
    ram = database.Column(database.Integer, nullable=False)
    storage = database.Column(database.Integer, nullable=False)
    is_active = database.Column(database.Boolean, default=True)
    category = database.Column(database.String(50), nullable=False)
    created_at = database.Column(database.DateTime, default = datetime.utcnow)

    __table_args__ = (
        database.UniqueConstraint("shop_id","name", "brand", name='unique_product_per_shop'),
    )

class Purchase(database.Model):
    __tablename__ = "Purchase_Data"
    id = database.Column(database.Integer, primary_key = True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"), nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("Products_Data.id"), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    supplier_name = database.Column(database.String(50), nullable=False)
    purchase_price = database.Column(database.Integer, nullable=False)
    purchase_date = database.Column(database.DateTime, default=datetime.utcnow)

    __table_args__ = (
        database.UniqueConstraint("shop_id", "product_id", name='no_repeation_in_stock'),
    )
    
class Sales(database.Model):
    __tablename__ = "Salses_Data"
    id = database.Column(database.Integer, primary_key = True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"), nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("Products_Data.id"))
    quantity = database.Column(database.Integer, nullable=False)
    purchase_price = database.Column(database.Integer, nullable=False)
    selling_price = database.Column(database.Integer, nullable=False)
    selling_date = database.Column(database.DateTime, default=datetime.utcnow)

    __table_args__ = (
        database.UniqueConstraint("shop_id", "product_id", name='no_repeation_in_sale'),
    )

class Expanses(database.Model):
    __tablename__ = "Expanses_Data"
    id = database.Column(database.Integer, primary_key=True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"))
    title = database.Column(database.String(50), nullable=False)
    note = database.Column(database.String(1000), nullable=False)
    amount = database.Column(database.Integer, nullable=False)
    expanse_type = database.Column(database.String, nullable=False, default='expanse')
    date = database.Column(database.Date, default=date.today)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)

class Subscription(database.Model):
    __tablename__ = "Subscription_Data"
    id = database.Column(database.Integer, primary_key=True)
    shop_id = database.Column(database.Integer, database.ForeignKey("Shops_Data.id"))
    start_at = database.Column(database.Date, default=date.today, nullable=False)
    end_at = database.Column(database.Date, nullable=False)
    plan_name = database.Column(database.String(50), nullable=False, default="trial")
    status = database.Column(database.String(50), nullable=False, default="trial")
    payment_id = database.Column(database.String(50), nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
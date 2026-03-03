

from flask import jsonify, request, Blueprint, make_response
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    jwt_required
)
from datetime import datetime
from .extensions import database
from .models import Users, Sales, Products, Purchase, OtherManages
import string, random

main_bp = Blueprint("main_bp", __name__)

def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
def current_user():
    user_id = get_jwt_identity()
    return Users.query.filter_by(user_code=user_id).first()

def get_date(data):
    if not data:
        return None
    try:
        return datetime.fromisoformat(data).date()
    except ValueError:
        return None

def lower_case(data):
    return (data or "").strip().lower()

def generate_shop_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@main_bp.route("/create_account", methods=["POST"])
def createAccount():
    data = request.get_json()
    if not data:
        return jsonify({"message" : "Please send valid data"})
    
    existing = Users.query.filter_by(user_email = data.get("user_email")).first()
    if existing:
        return jsonify({"message" : "Email already Exist"})
    
    user_name = lower_case(data.get("user_name"))
    user_email = lower_case(data.get("user_email"))
    user_code = generate_shop_code()
    if not user_email or not user_name:
        return jsonify({"message" : "Please enter valid name or email"})
    
    
    addingUser = Users(user_name = user_name, user_email = user_email, user_code = user_code)
    addingUser.encrypt_password(data.get("password"))
    database.session.add(addingUser)
    database.session.commit()
    return jsonify({"message" : "Account Created Successfullly", "Code" : user_code})

@main_bp.route("/login_user", methods=["POST"])
# @limiter.limit("5 per minute")
def loginUser():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Send data first"}), 400

    user_email = lower_case(data.get("user_email"))
    password = data.get("password")
    user_code = data.get("user_code")

    user = Users.query.filter_by(user_email=user_email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.check_encrypted_password(password) or user.user_code != user_code:
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.user_code), additional_claims={"user_id": user.id})
    refresh_token = create_refresh_token(identity=str(user.user_code), additional_claims={"user_id": user.id})

    response = make_response(jsonify({"login": True}))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200

@main_bp.route("/add_product", methods=["POST"])
@jwt_required()
def addProduct():
    user = current_user()
    data = request.get_json()

    name = lower_case(data.get("name"))
    brand = lower_case(data.get("brand"))
    category = lower_case(data.get("category"))

    existing = Products.query.filter_by(name=name, brand=brand, category=category, user_code=user.user_code).first()
    if existing:
        return jsonify({"message": "Product already exists"}), 400

    if not name or not category or not brand:
        return jsonify({"message": "Missing fields"}), 400

    product = Products(
        user_code = user.user_code,
        name=name,
        brand=brand,
        ram=to_int(data.get("ram")),
        storage=to_int(data.get("storage")),
        category=category,
        status="active"
    )

    database.session.add(product)
    database.session.commit()

    return jsonify({"message": "Product added Successfully"}), 200

@main_bp.route("/get_product", methods=["GET"])
@jwt_required()
def getProduct():
    user = current_user()
    products = Products.query.filter_by(user_code = user.user_code).all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "ram": p.ram,
            "storage": p.storage,
            "category": p.category,
            "status": p.status,
            "quantity": p.quantity,
            "created_at": p.created_at.isoformat()
        })

    return jsonify(result), 200

@main_bp.route("/fill_stock", methods=["POST"])
@jwt_required()
def addStock():
    data = request.get_json()
    user = current_user()
    product = Products.query.filter_by(id=data.get("product_id")).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    qty = int(data.get("quantity"))

    product.quantity += qty

    purchase = Purchase(
        user_code=user.user_code,
        product_id=product.id,
        quantity=qty,
        purchase_price=int(data.get("purchase_price")),
        supplier_name=data.get("supplier_name"),
        purchase_date=get_date(data.get("purchase_date"))
    )

    database.session.add(purchase)
    database.session.commit()

    return jsonify({"message": "Stock filled successfully"}), 200

@main_bp.route("/get_stock", methods=["GET"])
@jwt_required()
def getStock():
    user = current_user()
    stocks = Purchase.query.filter_by(user_code = user.user_code).all()
    return jsonify([
        {
            "id": s.id,
            "product_id": s.product_id,
            "quantity": s.quantity,
            "purchase_price": s.purchase_price,
            "supplier_name": s.supplier_name,
            "purchase_date": s.purchase_date.isoformat()
        }
        for s in stocks
    ])

@main_bp.route("/add_sale", methods=["POST"])
@jwt_required()
def addSale():
    data = request.get_json()
    user = current_user()

    product = Products.query.filter_by(id=data.get("product_id")).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    qty = int(data.get("quantity"))

    if product.quantity < qty:
        return jsonify({"message": "Insufficient stock"}), 400

    product.quantity -= qty

    sale = Sales(
        user_code = user.user_code,
        product_id=product.id,
        quantity=qty,
        selling_price=int(data.get("selling_price")),
        purchase_price=int(data.get("purchase_price")),
        selling_date=get_date(data.get("selling_date"))
    )
    database.session.add(sale)
    database.session.commit()
    return jsonify({"message": "Sale recorded"}), 200

@main_bp.route("/get_sale", methods=["GET"])
@jwt_required()
def getSale():
    user = current_user()
    sales = Sales.query.filter_by(user_code = user.user_code).all()

    return jsonify([
        {
            "id": s.id,
            "product_id": s.product_id,
            "quantity": s.quantity,
            "selling_price": s.selling_price,
            "purchase_price": s.purchase_price,
            "selling_date": s.selling_date.isoformat()
        }
        for s in sales
    ])

@main_bp.route("/get_other_manages", methods=["GET"])
@jwt_required()
def getOtherManages():
    user = current_user()

    items = OtherManages.query.filter_by(user_code = user.user_code).all()

    return jsonify([
        {
            "id": i.id,
            "title": i.title,
            "note": i.note,
            "amount": i.amount,
            "which_type": i.which_type,
            "date": i.date.isoformat()
        }
        for i in items
    ])
    
@main_bp.route("/add_other_manages", methods=["POST"])
@jwt_required()
def addManages():
    data = request.get_json()
    user = current_user()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    title = lower_case(data.get("title"))
    note = lower_case(data.get("note"))
    amount = data.get("amount")
    which_type = lower_case(data.get("which_type"))
    entry_date = get_date(data.get("date"))

    if not title or not amount or not which_type:
        return jsonify({"message": "Missing required fields"}), 400

    item = OtherManages(
        user_code = user.user_code,
        title=title,
        note=note,
        amount=int(amount),
        which_type=which_type,
        date=entry_date
    )

    database.session.add(item)
    database.session.commit()

    return jsonify({"message": "Entry added successfully"}), 200

@main_bp.route("/update_product", methods=["PUT"])
@jwt_required()
def updateProduct():
    data = request.get_json()
    user = current_user()

    product = Products.query.filter_by(id=data.get("id") , user_code = user.user_code).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    product.name = lower_case(data.get("name"))
    product.brand = lower_case(data.get("brand"))
    product.ram = data.get("ram")
    product.storage = data.get("storage")
    product.category = lower_case(data.get("category"))
    product.status = lower_case(data.get("status"))

    database.session.commit()
    return jsonify({"message": "Product updated"}), 200

@main_bp.route("/update_stock", methods=["PUT"])
@jwt_required()
def updateStock():
    data = request.get_json()
    user = current_user()
    stock = Purchase.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not stock:
        return jsonify({"message": "Stock not found"}), 404

    product = Products.query.get(stock.product_id)


    new_qty = int(data.get("quantity"))
    if new_qty < stock.quantity and product.quantity < new_qty:
        return jsonify({"message" : "Insufficient Stock"})
    else:
        product.quantity -= stock.quantity
        product.quantity += new_qty

    stock.quantity = new_qty
    stock.purchase_price = int(data.get("purchase_price"))
    stock.supplier_name = data.get("supplier_name")
    stock.purchase_date = get_date(data.get("purchase_date"))

    database.session.commit()
    return jsonify({"message": "Stock updated"}), 200
    
@main_bp.route("/update_sale", methods=["PUT"])
@jwt_required()
def updateSale():
    data = request.get_json()
    user = current_user()

    sale = Sales.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not sale:
        return jsonify({"message": "Sale not found"}), 404

    product = Products.query.get(sale.product_id)

    product.quantity += sale.quantity

    new_qty = int(data.get("quantity"))
    if product.quantity < new_qty:
        return jsonify({"message": "Insufficient stock"}), 400

    product.quantity -= new_qty

    sale.quantity = new_qty
    sale.selling_price = int(data.get("selling_price"))
    sale.purchase_price = int(data.get("purchase_price"))
    sale.selling_date = get_date(data.get("selling_date"))

    database.session.commit()
    return jsonify({"message": "Sale updated"}), 200
    
@main_bp.route("/update_other_manages", methods=["PUT"])
@jwt_required()
def updateOtherManages():
    data = request.get_json()
    user = current_user()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    item = OtherManages.query.filter_by(id=data.get("id"), user_code=user.user_code).first()

    if not item:
        return jsonify({"message": "Entry not found"}), 404

    item.title = lower_case(data.get("title"))
    item.note = lower_case(data.get("note"))
    item.amount = int(data.get("amount"))
    item.which_type = lower_case(data.get("which_type"))
    item.date = get_date(data.get("date"))

    database.session.commit()

    return jsonify({"message": "Entry updated successfully"}), 200

@main_bp.route("/delete_product", methods=["DELETE"])
@jwt_required()
def deleteProduct():
    data = request.get_json()
    user = current_user()

    product = Products.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    database.session.delete(product)
    database.session.commit()

    return jsonify({"message": "Product deleted"}), 200

@main_bp.route("/delete_stock", methods=["DELETE"])
@jwt_required()
def deleteStock():
    data = request.get_json()
    user = current_user()

    stock = Purchase.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not stock:
        return jsonify({"message": "Stock not found"}), 404

    product = Products.query.get(stock.product_id)

    # restore quantity
    product.quantity -= stock.quantity

    database.session.delete(stock)
    database.session.commit()

    return jsonify({"message": "Stock deleted"}), 200

@main_bp.route("/delete_sale", methods=["DELETE"])
@jwt_required()
def deleteSale():
    data = request.get_json()
    user = current_user()

    sale = Sales.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not sale:
        return jsonify({"message": "Sale not found"}), 404

    product = Products.query.get(sale.product_id)

    # restore stock
    product.quantity += sale.quantity

    database.session.delete(sale)
    database.session.commit()

    return jsonify({"message": "Sale deleted"}), 200

@main_bp.route("/delete_other_manages", methods=["DELETE"])
@jwt_required()
def deleteOtherManages():
    data = request.get_json()
    user = current_user()

    item = OtherManages.query.filter_by(id=data.get("id"), user_code=user.user_code).first()
    if not item:
        return jsonify({"message": "Data not found"}), 404

    database.session.delete(item)
    database.session.commit()

    return jsonify({"message": "Deleted"}), 200
@main_bp.route("/get_account", methods=["GET"])
@jwt_required()
def getAccount():
    users = current_user()
    user = Users.query.filter_by(user_code=users.user_code).first()

    return jsonify({
        "id": user.id,
        "user_name": user.user_name,
        "user_email": user.user_email,
        "user_code": user.user_code
    })

@main_bp.route("/delete_full_datas", methods=["GET"])
@jwt_required()
def deletefullDatas():
    data = request.get_json()
    item = Users.query.all()
    item1 = Products.query.all()
    item2 = Purchase.query.all()
    item3 = Sales.query.all()
    item4 = OtherManages.query.all()
    database.session.delete(item)
    database.session.delete(item1)
    database.session.delete(item2)
    database.session.delete(item3)
    database.session.delete(item4)
    database.session.commit()
    return jsonify({"message" : "Deleted"})

@main_bp.route("/ping")
def ping():
    return jsonify({"message": "pong"}), 200

@main_bp.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity()
    user = Users.query.filter_by(user_code=identity).first()
    access = create_access_token(
        identity=str(user.user_code),
        additional_claims={"user_id": user.id}
    )
    response = jsonify({"msg": "refreshed"})
    set_access_cookies(response, access)
    return response, 200

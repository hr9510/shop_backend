from .models import Shops, Users, Products, Purchase, Sales, Expanses, Subscription
from . import jsonify, request, Response, Blueprint, database, datetime, create_refresh_token, create_access_token, set_access_cookies, set_refresh_cookies, jwt_required, get_jwt, get_jwt_identity, date
import string , random
from sqlalchemy.exc import IntegrityError

main_bp = Blueprint("main_bp", __name__)

def get_time(data):
    if not data:
        return None
    try:
        return datetime.fromisoformat(data).date()
    except ValueError:
        return None

def generate_shop_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@main_bp.route("/add_shop", methods=["POST"])
def addShop():
    data = request.get_json()
    shopCode = generate_shop_code()

    if not data:
        return jsonify({"message" : "Please add some data first"})
    addingShop = Shops(shop_name=data.get("shop_name"), owner_name = data.get("owner_name"), owner_contact = data.get("owner_contact"), shop_address = data.get("shop_address"), 
                       shop_code = shopCode)
    database.session.add(addingShop)
    database.session.commit()
    return jsonify({
        "msg" : "Shop Registered Successfully",
        "shop_code" : shopCode})

@main_bp.route("/add_user", methods=["POST"])
def addUser():
    data = request.get_json()
    if not data:
        return jsonify({"message" : "Please add some data first"})
    shop_code = data.get("shop_code")
    if not shop_code:
        return jsonify({"message" : "Invalid Shop Code"})
    shop = Shops.query.filter_by(shop_code = shop_code).first()
    
    addingUser = Users(shop_id = shop.id ,user_name= data.get("user_name"), email = data.get("email"))
    addingUser.encryptPassword(data.get("password"))
    database.session.add(addingUser)
    database.session.commit()
    return jsonify({"message" : "User Registered Successfully"})

@main_bp.route("/login_user", methods=["POST"])
def loginUser():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message" : "Please enter email or password first"})
    user = Users.query.filter_by(email = email).first()
    if not user:
        return jsonify({"message" : "Please create account using this email first"})
    if user and user.checkPassword(password):
        accessToken = create_access_token(identity=str(user.id), additional_claims={"shop_id" : user.shop_id})
        refreshToken = create_refresh_token(identity=str(user.id), additional_claims={"shop_id" : user.shop_id})
        response = jsonify({"message" : "Login Successfull"})
        set_access_cookies(response, accessToken)
        set_refresh_cookies(response, refreshToken)
        return response
    else:
        return jsonify({"message": "INVALID CREDENTIALS"}), 401
    
@main_bp.route("/start_plan", methods=["POST"])
@jwt_required(refresh=True)
def startPlan():
    data = request.get_json()
    startTime = get_time(data.get("start_at"))
    endTime = get_time(data.get("end_at"))
    identity = get_jwt_identity()
    user = Users.query.get(identity)
    plan = Subscription.query.get(user.shop_id)
    if plan:
        plan.start_at = get_time(data.get("start_at"))
        plan.end_at = get_time(data.get("end_at"))
        plan.plan_name = data.get("plan_name")
        plan.status = data.get("status")
        plan.payment_id = data.get("payment_id")
        database.session.commit()
        return jsonify({"message" : "Plan Updated Successfully"})
    if not data:
        return jsonify({"message" : "No Data Available"})
    addingSubscription = Subscription(start_at = startTime, shop_id = user.shop_id, end_at = endTime, status = data.get("status"), plan_name = data.get("plan_name"), payment_id = data.get("payment_id"))
    database.session.add(addingSubscription)
    database.session.commit()
    return jsonify({"message" : "Plan Started"})

@main_bp.route("/add_product", methods=["POST"])
@jwt_required()
def addProduct():
    data = request.get_json()
    shop_id = int(get_jwt()["shop_id"])
    if not data:
        return jsonify({"message" : "Please send some data first"})
    
    try :
        addingProduct = Products(name = data.get("name").strip().lower(), shop_id=shop_id, brand = data.get("brand").strip().lower(), ram = data.get("ram"), storage = data.get("storage"), is_active = data.get("is_active"), category = data.get("category"))
        database.session.add(addingProduct)
        database.session.commit()
    except IntegrityError:
        database.session.rollback()
        return jsonify({"message" : "Product already exist"})
    return jsonify({"message" : "Product Added Successfully"})

@main_bp.route("/fill_stock", methods=["POST"])
@jwt_required()
def stockFilling():
    data = request.get_json()
    purchaseDate = get_time(data.get("purchase_date"))
    shop_id = int(get_jwt()["shop_id"])
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    if not data:
        return jsonify({"message" : "No Data Available"})
    check = Purchase.query.filter_by(shop_id = shop_id, product_id = product_id).first()
    if check:
        check.quantity += quantity
        database.session.commit()
        return jsonify({"message" : "Stock Update Successfully"})
    addingStock = Purchase(quantity = quantity,shop_id = shop_id, product_id = product_id, supplier_name = data.get("supplier_name") , purchase_price = data.get("purchase_price"), purchase_date = purchaseDate)
    database.session.add(addingStock)
    database.session.commit()
    return jsonify({"message" : "Stock Filled Successfully"})

@main_bp.route("/add_sale", methods=["POST"])
@jwt_required()
def addSale():
    data = request.get_json()
    sellDate = get_time(data.get("selling_date"))
    if not data:
        return jsonify({"message" : "No Data Available"})
    
    shop_id = int(get_jwt()["shop_id"])
    quantity = data.get("quantity")

    update_stock = Purchase.query.filter_by(
    product_id=data.get("product_id"),
    shop_id=shop_id
).first()
    
    if update_stock.quantity < quantity:
        return jsonify({"message" : "No Sufficient Stock"})
    addingSale = Sales(quantity = quantity, purchase_price = data.get("purchase_price"),shop_id = shop_id,product_id = data.get("product_id"), selling_price = data.get("selling_price"), selling_date = sellDate)
    database.session.add(addingSale)
    database.session.commit()

    update_stock.quantity -= quantity
    database.session.commit()
    return jsonify("Sales Added Successfully")

@main_bp.route("/add_expanse", methods=["POST"])
@jwt_required()
def addExpanse():
    data = request.get_json()
    dateDate = get_time( data.get("date"))
    shop_id = int(get_jwt()["shop_id"])
    if not data:
        return jsonify({"message" : "No Data Available"})
    addingExpanse = Expanses(title = data.get("title"), shop_id = shop_id, note = data.get("note"), amount = data.get("amount"), expanse_type = data.get("expanse_type"), date = dateDate)
    database.session.add(addingExpanse)
    database.session.commit()
    return jsonify({"message" : "Note Added Successfully"})
    
@main_bp.route("/get_shop",methods=["GET"])
@jwt_required()    
def getShop():
    shop_id = int(get_jwt()["shop_id"])
    data = Shops.query.filter_by(id = shop_id).first()
    if not data :
        return jsonify({"message" : "No data available"})
    data_list = {
        "shop_name" : data.shop_name,
        "owner_name" : data.owner_name,
        "owner_contact" : data.owner_contact,
        "shop_address" : data.shop_address,
        "created_at" : data.created_at
    }
    return jsonify(data_list)

@main_bp.route("/get_all_shop",methods=["GET"])
@jwt_required()    
def getAllShop():
    data = Shops.query.all()
    if not data :
        return jsonify({"message" : "No data available"})
    data_list = [{
        "shop_name" : d.shop_name,
        "owner_name" : d.owner_name,
        "owner_contact" : d.owner_contact,
        "shop_address" : d.shop_address,
        "created_at" : d.created_at
    }for d in data]
    return jsonify(data_list)

@main_bp.route("/get_user", methods=["GET"])
@jwt_required()
def getUser():
    shop_id = int(get_jwt()["shop_id"])
    data = Users.query.filter_by(shop_id = shop_id).first()
    if not data:
        return jsonify({"message" : "Please send some data first"})
    datalist = {
        "id" : data.id,
        "user_name" : data.user_name,
        "email" : data.email
    }
    return jsonify(datalist)

@main_bp.route("/get_all_user", methods=["GET"])
@jwt_required()
def getAllUser():
    data = Users.query.all()
    if not data:
        return jsonify({"message" : "Please send some data first"})
    datalist = [{
        "id" : d.id,
        "user_name" : d.user_name,
        "user_email" : d.email,
    } for d in data]
    return jsonify(datalist)

@main_bp.route("/get_product", methods=["GET"])
@jwt_required()
def getProduct():
    shopId = int(get_jwt()["shop_id"])
    data = Products.query.filter_by(shop_id = shopId)
    if not data:
        return jsonify({"message" : "No data available"})
    datalist = [{
        "id" : d.id,
        "name" : d.name,
        "brand" : d.brand,
        "ram" : d.ram,
        "storage" : d.storage,
        "category" : d.category,
        "is_active" : d.is_active,
        "created_at" : d.created_at
    } for d in data]
    return jsonify(datalist)



@main_bp.route("/get_stock", methods=["GET"])
@jwt_required()
def getStock():
    shopId = int(get_jwt()["shop_id"])
    data = Purchase.query.filter_by(shop_id = shopId).all()
    datalist = [{
            "product_id" : d.product_id,
            "quantity" : d.quantity,
            "supplier_name" : d.supplier_name,
            "purchase_price" : d.purchase_price,
            "purchase_date" : d.purchase_date
        }for d in data]
    return jsonify(datalist)

@main_bp.route("/get_sale", methods=["GET"])
@jwt_required()
def getSale():
    shopId = int(get_jwt()["shop_id"])
    data = Sales.query.filter_by(shop_id = shopId)
    if not data:
        return jsonify({"message" : "No Data Available"})
    sales_list = [{
        "product_id" : d.product_id,
        "quantity" : d.quantity,
        "purchase_price" : d.purchase_price,
        "selling_price" : d.selling_price,
        "selling_date" : d.selling_date
    } for d in data]
    return jsonify(sales_list)



@main_bp.route("/get_expanse", methods=["GET"])
@jwt_required()
def getExpanse():
    shopId = int(get_jwt()["shop_id"])
    data = Expanses.query.filter_by(shop_id = shopId)
    if not data:
        return jsonify({"message" : "No Data Available"})
    data_list = [{
        "title" : d.title,
        "note" : d.note,
        "amount" : d.amount,
        "expanse_type" : d.expanse_type,
        "date" : d.date,
        "created_at" : d.created_at
    }for d in data]
    return jsonify(data_list)


@main_bp.route("/get_plan", methods=["GET"])
@jwt_required()
def getPlain():
    shopId = int(get_jwt()["shop_id"])
    data = Subscription.query.filter_by(shop_id = shopId)
    data_list = {
        "id" : data.id,
        "shop_id" : data.shop_id,
        "start_at" : data.start_at,
        "start_at" : data.end_at,
        "plan_name" : data.plan_name,
        "status" : data.status,
        "payment_id" : data.payment_id,
        "created_at" : data.created_at
    }
    return jsonify(data_list)

@main_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity()
    user = Users.query.get(identity)
    check = Subscription.query.filter_by(shop_id = user.shop_id).first()
    if date.today()  <= check.end_at:
        new_access = create_access_token(identity=identity,
                                        additional_claims={
                                            "shop_id" : user.shop_id
                                        })
        
        response = jsonify({"message" : "Access Token Refreshed"})
        set_access_cookies(response, new_access)
        return response
    else:
        check.status="expired"
        check.plan_name="not active"
        database.session.commit()
        return jsonify({"message" : "Your plan has expired"})

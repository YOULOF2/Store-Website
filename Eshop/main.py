from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, LoginManager
from database import User, Products, db, get_time
from forms import LoginForm, SignUpForm, ModifyProduct, CreateProduct, ForgotPasswordForm, UpdatePassword
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from decorators import is_authenticated, not_authenticated, is_admin
from flask_ckeditor import CKEditor
from distutils.util import strtobool
from random import choice
from emails import send_pass_reset, decode_url

DATABASE_FILE_LOCATION = "database.db"
SALT_TIMES = 10

load_dotenv()


def create_app():
    flask_app = Flask(__name__)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    ckeditor = CKEditor(app=flask_app)

    flask_app.secret_key = getenv("SECRET_KEY")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_FILE_LOCATION}"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    database_file = Path(DATABASE_FILE_LOCATION)
    if not database_file.is_file():
        with flask_app.app_context():
            db.create_all()

    return flask_app


login_manager = LoginManager()
eshop = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@eshop.route("/")
def home():
    sort_type = request.args.get("sort")
    match sort_type:
        case "popular":
            query = db.session.query(Products)
            products = query.order_by(Products.quantity_sold)
            return render_template("shop/index.html", products=products)
        case "new":
            all_products = Products.query.all()
            day, month, year = get_time().split("/")
            today_datetime_obj = datetime(year=int(year), month=int(month), day=int(day))
            products = []
            for product in all_products:
                product_day, product_month, product_year = product.date_added.split("/")
                product_datetime_obj = datetime(year=int(product_year), month=int(product_month), day=int(product_day))
                if (product_datetime_obj - today_datetime_obj).days < 3:
                    products.append(product)

            return render_template("shop/index.html", products=products)

    products = Products.query.all()
    return render_template("shop/index.html", products=products)


# User =================================================================================================================
@eshop.route("/user/login", methods=["GET", "POST"])
@not_authenticated
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user_obj = User.query.filter_by(email=email).first()

            if user_obj is not None:
                is_pass_correct = check_password_hash(password=password, pwhash=user_obj.password)
                if is_pass_correct:
                    login_user(user_obj)
                    return redirect(url_for("home"))
                else:
                    flash("Wrong Password. Please Try Again")
                    return redirect(url_for("login"))
            else:
                flash("You don't have an account, please signup.")
                return redirect(url_for("signup"))
        else:
            flash("Please try again.")
            return redirect(url_for("login"))

    return render_template("auth/login.html", form=form)


@eshop.route("/user/signup", methods=["GET", "POST"])
@not_authenticated
def signup():
    form = SignUpForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            is_email_registered = True if User.query.filter_by(email=email).first() is not None else False
            if not is_email_registered:
                hashed_password = generate_password_hash(password, salt_length=SALT_TIMES)
                new_user = User(username=username, email=email, password=hashed_password)

                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                return redirect(url_for("home"))
            else:
                flash("You are already registered, please login.")
                return redirect(url_for("login"))
        else:
            flash("Please try again.")
            return redirect(url_for("signup"))

    return render_template("auth/signup.html", form=form)


@eshop.route("/user/logout")
@is_authenticated
def logout():
    logout_user()
    return redirect(url_for("home"))


@eshop.route("/user/password/forgot", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            found_user = True if User.query.filter_by(email=email).first() is not None else False
            if found_user:
                send_pass_reset(user_email=email)
                flash("Email Is sent to you, check your inbox!")
                return redirect(url_for("login"))
    return render_template("auth/forgot_password.html", form=form)


@eshop.route("/user/password/reset", methods=["GET", "POST"])
def reset_password():
    form = UpdatePassword()
    request_id = request.args.get("request_id")
    if request_id is None:
        flash("Invalid request url")
        return redirect(url_for("login"))
    decoded_id = decode_url(request_id)

    if request.method == "POST":
        # If request method is 'post'
        email = decoded_id.get("email")
        password = form.new_password.data
        user_obj = User.query.filter_by(email=email).first()
        hashed_password = generate_password_hash(password, salt_length=SALT_TIMES)
        user_obj.password = hashed_password
        db.session.commit()
        flash("Your password has been changed, you can login now!")
        return redirect(url_for("login"))
    else:
        # If request method is 'get'
        email_present = True if User.query.filter_by(email=decoded_id.get("email")).first() is not None else False
        time_accepted = True if decoded_id.get("time dif") <= 900 else False
        if email_present and time_accepted:
            return render_template("auth/update_password.html", form=form, request_id=request_id)

        if not email_present:
            flash("Invalid Email Inputted")
        elif not time_accepted:
            flash("Password reset expired")
        return redirect(url_for("login"))


@eshop.route("/user/wish-list")
@is_authenticated
def show_wish_list():
    user_obj = User.query.get(current_user.get_id())
    wish_list = user_obj.wish_list
    print(f"show with_list: {wish_list = }")
    return render_template("shop/wish-list.html", wish_list=wish_list)


@eshop.route("/user/wish-list/add")
@is_authenticated
def add_wish_list():
    user_obj = User.query.get(current_user.get_id())
    product_id = request.args.get("product_id")

    product_obj = Products.query.filter_by(product_id=product_id).first()
    user_obj.wish_list.append(product_obj)
    db.session.commit()

    return redirect(url_for("show_wish_list"))


@eshop.route("/user/wish-list/remove")
@is_authenticated
def remove_wish_list():
    user_obj = User.query.get(current_user.get_id())
    product_id = request.args.get("product_id")

    product_obj = Products.query.filter_by(product_id=product_id).first()
    for product in user_obj.wish_list:
        if product.product_id == product_obj.product_id:
            user_obj.wish_list.remove(product)
    db.session.commit()

    return redirect(url_for("show_wish_list"))


# Shopping Cart ========================================================================================================
@eshop.route("/cart")
@is_authenticated
def cart():
    current_user_id = current_user.get_id()
    user_obj = User.query.get(current_user_id)
    user_cart = user_obj.shopping_cart

    raw_sub_total = 0
    for product in user_cart:
        if product.on_sale:
            raw_sub_total += product.price_after_sale
        else:
            raw_sub_total += product.price
    # https://thepythonguru.com/python-string-formatting/
    sub_total = float("{:.2f}".format(raw_sub_total))
    return render_template("shop/cart.html", cart=user_cart, sub_total=sub_total)


@eshop.route("/cart/add")
@is_authenticated
def add_to_cart():
    product_id = request.args.get("product_id")
    product_obj = Products.query.filter_by(product_id=product_id).first()
    user_cart = current_user.shopping_cart

    user_cart.append(product_obj)
    db.session.commit()

    return redirect(url_for("home"))


@eshop.route("/cart/remove")
@is_authenticated
def remove_from_cart():
    product_id = request.args.get("product_id")
    product_obj = Products.query.filter_by(product_id=product_id).first()
    user_cart = current_user.shopping_cart

    if product_obj.product_id == product_id:
        for obj in user_cart:
            if obj.product_id == product_id:
                index = user_cart.index(obj)
                del user_cart[index]
        db.session.commit()

    return redirect(url_for("cart"))


@eshop.route("/cart/checkout")
@is_authenticated
def checkout():
    user_obj = User.query.get(current_user.get_id())
    shopping_cart = user_obj.shopping_cart


# Products =============================================================================================================
@eshop.route("/product")
def show_product():
    product_id = request.args.get("product_id")
    product_obj = Products.query.filter_by(product_id=product_id).first()
    return render_template("shop/product.html", product=product_obj)


@eshop.route("/product/modify", methods=["GET", "POST"])
@is_admin
def modify_product():
    product_id = request.args.get("product_id")
    item = Products.query.filter_by(product_id=product_id).first()
    form = ModifyProduct(
        product_name=item.name,
        desc=item.desc,
        quantity_available=item.quantity_available,
        on_sale=item.on_sale,
        price=item.price,
        price_after_sale=item.price_after_sale
    )
    if request.method == "POST":
        if form.validate_on_submit():
            new_product_name = form.product_name.data
            new_desc = form.desc.data
            new_quantity_available = form.quantity_available.data
            new_on_sale = bool(strtobool(form.on_sale.data))
            new_price = form.price.data
            new_price_after_sale = form.price_after_sale.data

            item.name = new_product_name
            item.desc = new_desc
            item.quantity_available = new_quantity_available
            item.on_sale = new_on_sale
            item.price = new_price
            item.price_after_sale = new_price_after_sale

            db.session.commit()
            return redirect(url_for("home"))
    return render_template("shop/edit_product.html", form=form, product_id=product_id)


@eshop.route("/product/create", methods=["POST", "GET"])
@is_admin
def create_product():
    form = CreateProduct()
    if request.method == "POST":
        if form.validate_on_submit():
            pictures = form.pictures.data.split(",")
            name = form.product_name.data
            description = form.desc.data
            quantity_available = form.quantity_available.data
            on_sale = bool(strtobool(form.on_sale.data))
            price = form.price.data
            price_after_sale = form.price_after_sale.data

            product_id = choice(str(uuid4()).split("-"))
            new_product = Products(
                product_id=product_id,
                name=name,
                desc=description,
                quantity_available=quantity_available,
                pictures=pictures,
                on_sale=on_sale,
                price_after_sale=price_after_sale,
                price=price
            )
            db.session.add(new_product)
            db.session.commit()

            return redirect(url_for("home"))

    return render_template("shop/create_product.html", form=form)


@eshop.route("/product/delete", methods=["GET"])
@is_admin
def remove_product():
    product_id = request.args.get("product_id")
    product_obj = Products.query.filter_by(product_id=product_id).first()
    db.session.delete(product_obj)
    db.session.commit()
    return redirect(url_for("home"))


if "__main__" == __name__:
    eshop.run(debug=True)

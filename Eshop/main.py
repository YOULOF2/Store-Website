from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, LoginManager
from database import User, Products, db, get_time
from forms import LoginForm, SignUpForm
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
from uuid import uuid4
from datetime import datetime

DATABASE_FILE_LOCATION = "database.db"
SALT_TIMES = 10

load_dotenv()


def create_app():
    flask_app = Flask(__name__)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

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
    return User.get(user_id)


@eshop.route("/")
def home():
    # for _ in range(50):
    #     new_product = Products(
    #         product_id=str(uuid4()).split("-")[0],
    #         pictures=["https://www.ubuy.com.bh/productimg/?image"
    #                   "=aHR0cHM6Ly9tLm1lZGlhLWFtYXpvbi5jb20vaW1hZ2VzL0kvNTFjR0NCeHFyUkwuX0FDX1NMMTAwMF8uanBn.jpg"],
    #         name="Teddy Bear",
    #         desc=" Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    #         quantity_available=10,
    #         price=10.00,
    #         rating=3
    #     )
    #     db.session.add(new_product)
    #     db.session.commit()

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


@eshop.route("/user/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user_obj = User.query.filter_by(email=email).first()

            if user_obj is not None:
                is_pass_correct = check_password_hash(password=password, pwhash=user_obj.passsword)
                if is_pass_correct:
                    login_user(current_user)
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
def signup():
    form = SignUpForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            is_email_registered = True if User.query.filter_by(email=email) is not None else False
            if not is_email_registered:
                hashed_password = generate_password_hash(password, salt_length=SALT_TIMES)
                new_user = User(username=username, email=email, password=hashed_password)

                db.session.commit(new_user)

                login(current_user)
            else:
                flash("You are already registered, please login.")
                return redirect(url_for("login"))
        else:
            flash("Please try again.")
            return redirect(url_for("signup"))

    return render_template("auth/signup.html", form=form)


@eshop.route("/admin")
def admin():
    return render_template("admin/index.html")


if "__main__" == __name__:
    eshop.run(debug=True)

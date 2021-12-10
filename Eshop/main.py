from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, LoginManager
from database import User, Products, db
from forms import LoginForm, SignUpForm
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

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
    return render_template("shop/index.html")


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


if "__main__" == __name__:
    eshop.run(debug=True)

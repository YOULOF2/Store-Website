from flask import Blueprint, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from ..database import User

SALT_TIMES = 10

class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login!")


class SignUp(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("SignUp!")


auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/user/login", methods=["GET", "POST"])
def login():
    form = Login()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.name
            password = form.password.name
            user_obj = User.query.filter_by(email=email).first()

            if user_obj is not None:
                is_pass_correct = check_password_hash(password=password, pwhash=user_obj.passsword)
                if is_pass_correct:
                    login_user(current_user)
                else:
                    # TODO: flash message on screen and return render_template
                    pass

    return render_template("login.html", form=form)


@auth.route("/user/signup", methods=["GET", "POST"])
def signup():
    form = SignUp()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.name
            email = form.email.name
            password = form.password.name
    return render_template("signup.html", form=form)

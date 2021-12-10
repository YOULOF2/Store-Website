from flask import Blueprint, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

from Eshop.database import User, db 

SALT_TIMES = 10


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class SignUpForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/user/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        print(f"{form.validate_on_submit() = }")
        print(form.errors)
        if form.validate_on_submit():
            print('User logging in')
            email = form.email.data
            password = form.password.data
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
    form = SignUpForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # username = form.username.data
            # email = form.email.data
            # password = form.password.data
            print("Signup done")
    return render_template("signup.html", form=form)

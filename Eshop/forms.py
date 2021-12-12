from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditor


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class SignUpForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class ModifyProduct(FlaskForm):
    product_name = StringField(label="Product name", validators=[DataRequired()])
    desc = CKEditor("Description")

    quantity_available = IntegerField(label="Quantity available", validators=[DataRequired()])
    on_sale = BooleanField(label="On sale", validators=[DataRequired()])
    price = FloatField(label="Price", validators=[DataRequired()])
    price_after_sale = FloatField(label="Price after sale", validators=DataRequired())


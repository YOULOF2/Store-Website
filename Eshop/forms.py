from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, FloatField, RadioField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class SignUpForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class ForgotPasswordForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    submit = SubmitField()


class UpdatePassword(FlaskForm):
    new_password = StringField(validators=[DataRequired()])
    submit = SubmitField()


class ModifyProduct(FlaskForm):
    product_name = StringField(label="Product name", validators=[DataRequired()])
    desc = CKEditorField(label="Description")

    quantity_available = IntegerField(label="Quantity available", validators=[DataRequired()])
    on_sale = SelectField(label="On sale", choices=["True", "False"])
    price = FloatField(label="Price", validators=[DataRequired()])
    price_after_sale = FloatField(label="Price after sale", default=0.0)
    submit = SubmitField(label="Update Product")


class CreateProduct(FlaskForm):
    pictures = StringField(label="Images")
    product_name = StringField(label="Product name", validators=[DataRequired()])
    desc = CKEditorField(label="Description")

    quantity_available = IntegerField(label="Quantity available", validators=[DataRequired()])
    on_sale = SelectField(label="On sale", choices=["True", "False"])
    price = FloatField(label="Price", validators=[DataRequired()])
    price_after_sale = FloatField(label="Price after sale", default=0.0)
    submit = SubmitField(label="Create Product")

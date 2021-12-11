from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


def get_time():
    datetime_obj = datetime.now()
    formated_datetime = datetime_obj.strftime("%d/%m/%Y")
    return str(formated_datetime)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    # The list will have dicts with product ids and count
    shopping_cart = db.Column(MutableList.as_mutable(PickleType), default=[])

    wish_list = db.Column(MutableList.as_mutable(PickleType), default=[])


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, nullable=False, unique=True)
    pictures = db.Column(MutableList.as_mutable(PickleType), default=[])
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)

    quantity_available = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False, default=0)
    date_added = db.Column(db.Text, nullable=False, default=get_time())

    on_sale = db.Column(db.Boolean, nullable=False, default=False)
    price_after_sale = db.Column(db.Float, nullable=True, default=0)
    price = db.Column(db.Float, nullable=False)

    rating = db.Column(db.Integer, nullable=False, default=0)


class Sales(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)

    items_sold = db.Column(db.Integer, nullable=False, default=0)
    total_profit = db.Column(db.Integer, nullable=False, default=0.0)

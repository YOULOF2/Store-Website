from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from flask_login import UserMixin

db = SQLAlchemy()


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

    product_id = db.Column(db.Integer, nullable=False)
    pictures = db.Column(MutableList.as_mutable(PickleType), default=[])
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

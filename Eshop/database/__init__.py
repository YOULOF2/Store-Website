from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DATABASE_FILE_LOCATION = "database/database.db"
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    pic_link = db.Column(db.Text, nullable=True)
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)


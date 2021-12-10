from flask import Flask, redirect, url_for
from os import getenv
from pathlib import Path

from shop import shop
from auth import auth as auth_app
from Eshop.database import db

from dotenv import load_dotenv

load_dotenv()

DATABASE_FILE_LOCATION = "database/database.db"


def create_app():
    flask_app = Flask(__name__)
    db.init_app(flask_app)

    flask_app.register_blueprint(shop)
    flask_app.register_blueprint(auth_app)
    flask_app.secret_key = getenv("SECRET_KEY")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_FILE_LOCATION}"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    database_file = Path(DATABASE_FILE_LOCATION)
    print(database_file.is_file())
    if not database_file.is_file():
        with flask_app.app_context():
            db.create_all()

    return flask_app


app = create_app()


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if "__main__" == __name__:
    app.run(debug=True)

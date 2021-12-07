from flask import Flask, redirect, url_for
from os import getenv
from pathlib import Path

from shop import shop
from auth import auth
from database import db as root_db, DATABASE_FILE_LOCATION

from dotenv import load_dotenv
load_dotenv()


def create_app():
    flask_app = Flask(__name__)
    root_db.init_app(app)

    flask_app.register_blueprint(shop)
    flask_app.register_blueprint(auth)
    flask_app.secret_key = getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{DATABASE_FILE_LOCATION}"

    database_file = Path(DATABASE_FILE_LOCATION)
    if not database_file.is_file():
        with app.app_context():
            root_db.create_all()

    return flask_app


app = create_app()


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if "__main__" == __name__:
    app.run(debug=True)

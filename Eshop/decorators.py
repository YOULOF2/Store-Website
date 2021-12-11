from flask_login import current_user
from flask import redirect, url_for
from functools import wraps


def not_authenticated(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("home"))

    return wrapper


def is_authenticated(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrapper

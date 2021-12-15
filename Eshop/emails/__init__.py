import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from cryptography.fernet import Fernet
from datetime import datetime
from flask import url_for, request
from pathlib import Path
import jinja2
from dotenv import load_dotenv

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
KEY = str.encode(os.getenv("CIPHER_KEY"))
CIPHER_KEY = Fernet(KEY)


def create_request_id(user_email):
    formatted_time = datetime.now().strftime("%m/%d/%Y|%H:%M:%S")
    raw_id = f"{user_email}-{formatted_time}"
    raw_id_bytes = str.encode(raw_id)
    request_id = CIPHER_KEY.encrypt(raw_id_bytes)
    return request_id


def decode_url(request_id):
    request_id_bytes = str.encode(request_id)
    decrypted_id = CIPHER_KEY.decrypt(request_id_bytes)
    raw_id = decrypted_id.decode()
    email, date_time = raw_id.split("-")
    date, time = date_time.split("|")

    day, month, year = date.split("/")
    hour, minute, seconds = time.split(":")

    current_time = datetime.now()
    datetime_obj = datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=seconds)

    to_return = {
        "time dif": (datetime_obj - current_time).total_seconds(),
        "email": email
    }

    return to_return


def send_pass_reset(user_email):
    def generate_recovery_email():
        endpoint = url_for("reset_password", request_id=request_id)
        return f"{request.url_root}{endpoint}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset"
    message["From"] = SENDER_EMAIL
    message["To"] = user_email

    request_id = create_request_id(user_email)
    recovery_url = generate_recovery_email()

    text_body = f"Hello, you requested a password reset," \
                f"If you didn't request a new password, you can safely delete this email.\n" \
                f"please visit this url to reset password:\n{recovery_url}"

    template_loader = jinja2.FileSystemLoader(searchpath=str(Path(Path(__file__).parent)))
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("password_reset.html")
    html_body = template.render(recovery_url=recovery_url)

    plain_text = MIMEText(text_body, "plain")
    html_text = MIMEText(html_body, "html")

    message.attach(plain_text)
    message.attach(html_text)

    smt = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
    smt.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
    smt.ehlo()
    smt.sendmail(SENDER_EMAIL, user_email, message.as_string())
    smt.quit()
#

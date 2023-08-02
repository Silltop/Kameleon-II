import secrets
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

def generate_random_secret_key(length):
    if length % 2 != 0:
        raise ValueError("Length should be an even number.")
    return secrets.token_hex(length // 2)


template_dir = "./templates"
static_dir = "./static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = generate_random_secret_key(32)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/db/kameleon.db"
db = SQLAlchemy()
db.init_app(app)
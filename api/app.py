import glob
import os
import secrets

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy


def generate_random_secret_key(length):
    if length % 2 != 0:
        raise ValueError("Length should be an even number.")
    return secrets.token_hex(length // 2)


def find_extensions_templates():
    base_dir = os.path.join(os.getcwd(), "extensions")
    # Define the pattern to look for template directories
    pattern = os.path.join(base_dir, "*", "templates")
    # Use glob to find all directories that match the pattern
    template_dirs = glob.glob(pattern)
    # Now, the template_dirs variable will contain a list of full paths to the template directories
    return template_dirs


config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}
template_dir = "../templates"
static_dir = "../static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = generate_random_secret_key(32)
for directory in find_extensions_templates():
    app.jinja_loader.searchpath.append(directory)
app.jinja_loader.searchpath.append(
    os.path.join(os.getcwd(), "ansible_wrapper/templates")
)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/db/kameleon.db"
db = SQLAlchemy()
db.init_app(app)
app.config.from_mapping(config)
cache = Cache(app)

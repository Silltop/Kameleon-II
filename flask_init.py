from flask import Flask

template_dir = "./templates"
static_dir = "./static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/db/kameleon.db"
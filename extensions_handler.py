import importlib
import json
import logging
import os

from web.app import db
from data_management.db_models import ExtensionRoutes


# todo make blueprints for remote web and local web
# https://flask.palletsprojects.com/en/3.0.x/blueprints/
def init_extensions():
    # Define the path to the extensions directory
    extensions_dir = "extensions"
    # cleanup all extensions on start up
    db.session.query(ExtensionRoutes).delete()
    # List all directories (potential extensions) inside the extensions directory
    extensions = [
        d
        for d in os.listdir(extensions_dir)
        if os.path.isdir(os.path.join(extensions_dir, d))
    ]
    # Iterate over each extension and import its __init__.py
    logging.info("Searching for extensions...")
    for extension in extensions:
        json_file = os.path.join(extensions_dir, extension, "definition.json")
        if os.path.isfile(json_file):
            with open(json_file, "r") as f:
                json_data = json.loads(f.read())
                extension_name = json_data["name"]
                logging.info(f"Extension found: {extension_name}")
                routes = json_data["routes"]
                for routename, route in routes.items():
                    exists = ExtensionRoutes.query.filter_by(route_name=routename).first()
                    if not exists:
                        er = ExtensionRoutes(
                            extension_name=extension_name, route_name=routename, route_endpoint=route
                        )
                        db.session.add(er)
            db.session.commit()
            extension_module = importlib.import_module(f"{extensions_dir}.{extension}")
            db.create_all()
    logging.info("Extensions lookup done")


# def create_prefixed_table(model_class, prefix='extension_'):
#     table_name = prefix + model_class.__name__.lower()
#
#     # Create the table
#     columns = []
#     for column in model_class.__table__.columns:
#         columns.append(column.copy())
#
#     table = type(table_name, (db.Model,), {
#         '__tablename__': table_name,
#         '__module__': model_class.__module__,
#         'id': db.Column(db.Integer, primary_key=True),
#         **{column.name: column for column in columns}
#     })
#
#     # Add the table to the metadata
#     db.metadata.create_all(db.engine, tables=[table.__table__])
#
# def create_table(model_class):
#     create_prefixed_table(model_class)

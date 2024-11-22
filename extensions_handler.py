import json
import logging
import os
import importlib

from data_management.db_models import ExtensionRoutes
from api.app import db


# todo make blueprints for remote api and local api
# https://flask.palletsprojects.com/en/3.0.x/blueprints/
def init_extensions():
    # Define the path to the extensions directory
    extensions_dir = 'extensions'
    # cleanup all extensions on start up
    db.session.query(ExtensionRoutes).delete()
    # List all directories (potential extensions) inside the extensions directory
    extensions = [d for d in os.listdir(extensions_dir) if os.path.isdir(os.path.join(extensions_dir, d))]
    # Iterate over each extension and import its __init__.py
    logging.info("Searching for extensions...")
    for extension in extensions:
        json_file = os.path.join(extensions_dir, extension, 'definition.json')
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                json_data = json.loads(f.read())
                name = json_data['name']
                exists = ExtensionRoutes.query.filter_by(name=name).first()
                if not exists:
                    er = ExtensionRoutes(name=json_data['name'], route=json_data['route'])
                    logging.info(f"Extension found: {name}")
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

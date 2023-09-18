import json
import os
import importlib

from db_models import ExtensionRoutes
from flask_init import db

def init_extensions():
    # Define the path to the extensions directory
    extensions_dir = 'extensions'
    # List all directories (potential extensions) inside the extensions directory
    extensions = [d for d in os.listdir(extensions_dir) if os.path.isdir(os.path.join(extensions_dir, d))]
    # Iterate over each extension and import its __init__.py
    for extension in extensions:
        json_file = os.path.join(extensions_dir, extension, 'definition.json')
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                json_data = json.loads(f.read())
                name=json_data['name']
                exists = ExtensionRoutes.query.filter_by(name=name).first()
                if not exists:
                    er = ExtensionRoutes(name=json_data['name'], route=json_data['route'])
                    print(json_data)
                    db.session.add(er)
            db.session.commit()
            extension_module = importlib.import_module(f"{extensions_dir}.{extension}")
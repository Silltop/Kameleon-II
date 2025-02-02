import importlib
import json
import logging
import os
from web.app import db
from data_management.db_models import ExtensionRoutes
from web.app import app


class ExtensionHandler:
    def __init__(self, extensions_dir="extensions"):
        self.extensions_dir = extensions_dir

    def init_extensions(self):
        self.cleanup_extensions()
        extensions = self.list_extensions()
        logging.info("Searching for extensions...")
        for extension in extensions:
            self.process_extension(extension)
        logging.info("Extensions lookup done")

    def cleanup_extensions(self):
        db.session.query(ExtensionRoutes).delete()

    def list_extensions(self):
        return [d for d in os.listdir(self.extensions_dir) if os.path.isdir(os.path.join(self.extensions_dir, d))]

    def process_extension(self, extension):
        json_file = os.path.join(self.extensions_dir, extension, "definition.json")
        if os.path.isfile(json_file):
            with open(json_file, "r") as f:
                json_data = json.loads(f.read())
                extension_name = json_data["name"]
                logging.info(f"Extension found: {extension_name}")
                routes = json_data["routes"]
                self.register_routes(extension_name, routes)
            self.import_extension_module(extension, extension_name)
            self.log_registered_routes()
            db.create_all()

    def register_routes(self, extension_name, routes):
        for routename, route in routes.items():
            exists = ExtensionRoutes.query.filter_by(route_name=routename).first()
            if not exists:
                er = ExtensionRoutes(extension_name=extension_name, route_name=routename, route_endpoint=route)
                db.session.add(er)
        db.session.commit()

    def import_extension_module(self, extension, extension_name):
        extension_module = importlib.import_module(f"{self.extensions_dir}.{extension}.functions")
        if hasattr(extension_module, "plugin"):
            blueprint = getattr(extension_module, "plugin")
            logging.info(f"Registering blueprint for extension: {extension_name}")
            app.register_blueprint(blueprint)

    def log_registered_routes(self):
        for rule in app.url_map.iter_rules():
            logging.info(f"Route registered: {rule.endpoint} -> {rule.rule}")

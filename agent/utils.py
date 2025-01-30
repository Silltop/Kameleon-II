import importlib.util
import logging
import os
import subprocess
from flask import Blueprint
from api import app

extensions_dir = './extensions'

def run_command(command: str, default: str = "default output") -> str:
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        output = ' '.join(result.stdout.split())  # Merge all lines into a single string
        return output if output else default
    except subprocess.CalledProcessError as e:
        # If the command fails, raise an exception with error details
        logging.error(f"Command failed: {e.stderr}")
        return "error"


def register_blueprints() -> None:
    # Loop through each directory in the 'extensions' directory
    for dirpath, dirnames, filenames in os.walk(extensions_dir):
        # Check if there is an 'endpoints.py' in the current directory
        if 'endpoints.py' in filenames:
            # Construct the full path to 'endpoints.py'
            module_path = os.path.join(dirpath, 'endpoints.py')

            # Dynamically import the 'endpoints.py' module
            module_name = f"extension_{os.path.basename(dirpath)}"  # Unique module name
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Loop through the attributes in the module and register blueprints
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                # If the attribute is a Blueprint, register it
                if isinstance(attribute, Blueprint):
                    app.register_blueprint(attribute)

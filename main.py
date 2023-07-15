from flask import render_template

# from ansible_wrapper import check_service_status
from flask_init import app
import logging_setup
import flask_routes

# # Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app.run(debug=True, use_reloader=True)

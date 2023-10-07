import schedule
from flask import render_template

import db_models
import extensions_handler
# from ansible_wrapper import check_service_status
from flask_init import app
import logging_setup
import flask_routes
import sync_functions

# # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import logging
    logging.info("Kameleon starting up...")
    pssh_logger = logging.getLogger("pssh")
    pssh_logger.setLevel(logging.CRITICAL)
    with app.app_context():
        db_models.init_db_tables_with_data()
        extensions_handler.init_extensions()
    #loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    #print(loggers)
    schedule.every(5).minutes.do(sync_functions.sync_all)
    app.run(debug=True, use_reloader=False)

import atexit
import time
from threading import Event, Thread

import schedule

from ansible_wrapper import ansible_init, ansible_routes  # noqa E401
from ansible_wrapper.ansible_routes import ansible  # noqa E401
from configuration import logger, setup_logging
from data_management import db_models, sync_functions
from extensions_handler import ExtensionHandler
from web import app


def run_scheduled_jobs(event):
    while not event.is_set():
        schedule.run_pending()
        time.sleep(1)


# stop the background task gracefully before exit
def stop_background_threads(stop_event, threads: list):
    logger.info("At exit stopping background threads...")
    # request the background thread stop
    stop_event.set()
    # wait for the background thread to stop
    for thread in threads:
        thread.join()
    logger.info("At exit threads shutdown complete.")


if __name__ == "__main__":
    setup_logging()
    stop_event = Event()
    eh = ExtensionHandler()
    logger.info("Kameleon starting up...")
    with app.app_context():
        db_models.init_db_tables_with_data()
        eh.init_extensions()
    schedule.every(1).minutes.do(sync_functions.sync_all)
    scheduler_thread = Thread(target=run_scheduled_jobs, args=(stop_event,), daemon=True, name="TaskExecutor")
    scheduler_thread.start()
    atexit.register(stop_background_threads, stop_event, [scheduler_thread])
    app.register_blueprint(ansible)
    app.run(host="0.0.0.0", debug=True, use_reloader=True)

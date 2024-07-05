import threading
import time
import logging
from .utils import fetch_teams_data

logger = logging.getLogger(__name__)

def start_periodic_task(interval):
    def run_task():
        while True:
            logger.info('Ejecutando fetch_teams_data...')
            fetch_teams_data()
            logger.info('fetch_teams_data ejecutado con éxito')
            time.sleep(interval)

    thread = threading.Thread(target=run_task)
    thread.daemon = True
    thread.start()

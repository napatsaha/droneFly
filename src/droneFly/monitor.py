import csv
import logging
import os
import threading
import time
import datetime

from djitellopy import Tello

from droneFly.base import BaseWorker
from droneFly import DATA_DIR

logger = logging.getLogger(__name__)



class DataCollector(BaseWorker):

    t0: float
    state_keys = [
        'pitch', 'roll', 'yaw', 'vgx', 'vgy', 'vgz', 'templ', 'temph',
        'tof', 'h', 'bat', 'baro', 'time', 'agx', 'agy', 'agz'
    ]

    def __init__(self,
                 drone: Tello,
                 stopper: threading.Event,
                 fps: int,
                 **kwargs):
        super().__init__(stopper, fps, **kwargs)
        self.drone = drone
        # self.logger = logger

        # File creation based on current date time
        date_dir = datetime.datetime.now().strftime("%Y-%m-%d")

        path = os.path.join(DATA_DIR, date_dir)
        if not os.path.exists(path):
            os.mkdir(path)

        filename = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f") + ".csv"
        filename = os.path.join(path, filename)
        self.csvfile = open(filename, 'w', newline='')

        # Set up csv writer
        self.writer = csv.DictWriter(self.csvfile, fieldnames=['time_elapsed'] + self.state_keys)
        self.writer.writeheader()

    def _run(self):
        time_elapsed = time.time() - self.t0
        state = self.drone.get_current_state()
        state['time_elapsed'] = f"{time_elapsed:.3f}"
        self.writer.writerow(state)

    def start(self) -> None:
        self.t0 = time.time()
        super().start()

    def close(self):
        super().close()
        logger.info("CSV file recorded as %s" % os.path.split(os.path.realpath(self.csvfile.name))[-1])
        self.csvfile.close()

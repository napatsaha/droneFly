import csv
import logging
import os
import threading
import time
import datetime

from djitellopy import Tello

from droneFly.base import BaseWorker


DIR_NAME = "../data"


class DataCollector(BaseWorker):

    t0: float

    def __init__(self,
                 drone: Tello,
                 stopper: threading.Event,
                 fps: int,
                 **kwargs):
        super().__init__(stopper, fps, **kwargs)

        filename = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f") + ".csv"
        filename = os.path.join(DIR_NAME, filename)
        self.csvfile = open(filename, 'w', newline='')

        self.drone = drone

        state = [
            'pitch', 'roll', 'yaw', 'vgx', 'vgy', 'vgz', 'templ', 'temph',
            'tof', 'h', 'bat', 'baro', 'time', 'agx', 'agy', 'agz'
        ]
        self.writer = csv.DictWriter(self.csvfile, fieldnames=['time_elapsed'] + state)
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
        logging.info("CSV file recorded as %s" % os.path.split(os.path.realpath(self.csvfile.name))[-1])
        self.csvfile.close()

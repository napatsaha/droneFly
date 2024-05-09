import logging
import time
import csv
from typing import Tuple

from djitellopy import Tello


class Timer:
    def __init__(self, duration):
        self.duration = duration

    def start(self):
        logging.info("Start timing")
        self.initial = time.time()

    def is_valid(self) -> bool:
        valid = time.time() - self.initial < self.duration
        return valid


class Controller:
    """
    Class for setting instructions to control flight of Tello drone, via
    RC controls (left, forward, up, yaw) and duration instructions stored in a file.

    Read from a csv file. Each row contains five values:
    - Left/Right Speed
    - Forward/Backward Speed
    - Up/Down Speed
    - Yaw (Angular rotation) Speed
    - Duration to perform the maneuver

    """

    drone: Tello
    timer: Timer
    current_control: Tuple

    def __init__(self, drone: Tello, filename: str, fps: int):
        self.file = open(filename, 'r')
        self.reader = csv.reader(self.file, delimiter=',')

        self.drone = drone
        self.fps = fps

    def _read(self) -> tuple:
        row = next(self.reader)
        rc = [int(val) for val in row[:4]]
        dur = float(row[-1])
        return rc, dur

    def next(self):
        rc, dur = self._read()
        self.timer = Timer(duration=dur)
        self.current_control = rc

    def execute(self):
        self.timer.start()
        self.drone.send_rc_control(*self.current_control)
        while self.timer.is_valid():
            time.sleep(1/self.fps)

    def run(self):
        while True:
            try:
                self.next()
                self.execute()
            except StopIteration:
                break

    def close(self):
        self.file.close()

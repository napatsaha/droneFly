import logging
import threading
import csv

from djitellopy import Tello


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
    # timer: Timer
    # current_control: Tuple

    def __init__(self, drone: Tello, filename: str, fps: int):
        self.file = open(filename, 'r')
        self.reader = csv.reader(self.file, delimiter=',')

        # self._stopped = False
        self.drone = drone
        self.fps = fps

    def read_next_line(self) -> tuple:
        row = next(self.reader)
        rc = [int(val) for val in row[:4]]
        dur = float(row[-1])
        return rc, dur

    # def next(self):
    #     rc, dur = self._read()
    #     self.timer = Timer(duration=dur)
    #     self.current_control = rc

    def process_movement(self, rc, dur, e):
        logging.info("Sending control {} for {} seconds".format(rc, dur))

        self.drone.send_rc_control(*rc)

        e.wait(dur)

    def run(self, event: threading.Event):
        logging.info("Beginning Movement Procedures")
        while not event.is_set():

            try:
                rc, dur = self.read_next_line()
                self.process_movement(rc, dur, event)
            except StopIteration:
                logging.info("Ended movement execution")
                break

        if not event.is_set():
            logging.info("Setting Termination Event due to completion of movement")
            event.set()

    # def stop(self):
    #     logging.info("Movement stopped abruptly")
    #     self._stopped = True

    def close(self):
        logging.info("Terminating Movement Handler")
        self.file.close()

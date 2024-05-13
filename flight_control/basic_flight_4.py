"""
Movement instructions control
using Event to terminate threads
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""


import time, csv, os
import threading
import logging
import signal

from djitellopy import Tello

from analysis import aggregate, detector
from flight_control.collision import CollisionDetector
# from flight_control.movement import Controller


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


# class ExitCommand(Exception):
#     pass
#
#
# def signal_handler(signalnum, frame):
#     logging.info("Signal Called")
#
#     raise ExitCommand()


def collision_handler(event: threading.Event):
    global drone, FPS, controller

    logging.info("Beginning Collision Handling")

    while not event.is_set():
        state = drone.get_current_state()

        collide = collision_detector(state)

        if collide:
            logging.info("Collided")
            break

        time.sleep(1/FPS)

    if not event.is_set():
        logging.info("Setting Termination Event due to collision")
        event.set()


FPS = 20
MAX_WAIT = 30

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
                    datefmt="%H:%M:%S")

# logger = logging.getLogger("ZScorer")
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

# signal.signal(signal.SIGTERM, signal_handler)

terminate = threading.Event()
drone = Tello()


metric = ["agx", "agy", "agz"]
aggregator = aggregate.MultiDiffAggregator(window=5, metrics=metric)
peaker = detector.ZScorePeakDetection(window=20, threshold=15, influence=0.1)
collision_detector = CollisionDetector(aggregator, peaker)

collision_thread = threading.Thread(target=collision_handler, name="Collision", args=(terminate,))


controller = Controller(drone, "move2.csv", fps=FPS)

movement_thread = threading.Thread(target=controller.run, name="Movement", args=(terminate,))

# Establish connection
drone.connect()


try:
    logging.info("Taking Off")
    drone.takeoff()

    collision_thread.start()

    movement_thread.start()

    # collision_thread.join()
    # movement_thread.join()
    terminate.wait(MAX_WAIT)

finally:

    controller.close()

    drone.land()

    # logging.info("Battery remaining %s", drone.get_battery())
    print(f"Battery: {drone.get_battery()}%")

    drone.end()


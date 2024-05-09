"""
Single control (with initial ascent)
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""


import time, csv, os
import threading
import logging
import signal

from djitellopy import Tello

from analysis import aggregate, detector
from flight_control.collision import CollisionDetector
from flight_control.movement import Controller


class MainTimer:
    def __init__(self, duration):
        self.duration = duration

    def start(self):
        logging.info("Start timing")
        self.initial = time.time()

    def is_valid(self) -> bool:
        valid = time.time() - self.initial < self.duration
        return valid


class ExitCommand(Exception):
    pass


def signal_handler(signalnum, frame):
    logging.info("Signal Called")

    raise ExitCommand()


def collision_handler():
    # global drone, FPS

    logging.info("Beginning Collision Handling")
    while True:
        state = drone.get_current_state()

        collide = collision_detector(state)

        if collide:
            logging.info("Collided")
            break

        time.sleep(1/FPS)

    signal.raise_signal(signal.SIGTERM)
    logging.info("Terminating Collision Handling")


FPS = 20
FLY_DURATION = 60
# FLIGHT_NAME = "Curved"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s -- %(threadName)s -- %(msg)s",
                    datefmt="%H:%M:%S")

logger = logging.getLogger("ZScorer")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

signal.signal(signal.SIGTERM, signal_handler)
# main_timer = MainTimer(duration=FLY_DURATION)

metric = ["agx", "agy", "agz"]
aggregator = aggregate.MultiDiffAggregator(window=5, metrics=metric)
peaker = detector.ZScorePeakDetection(window=20, threshold=20, influence=0.1)
collision_detector = CollisionDetector(aggregator, peaker)
collision_thread = threading.Thread(target=collision_handler, name="Collision")

# ascent_timer = MainTimer(duration=3)


drone = Tello()

controller = Controller(drone, "move1.csv", fps=FPS)

movement_thread = threading.Thread(target=controller.run, name="Movement")

drone.connect()


try:
    logging.info("Taking Off")
    drone.takeoff()

    collision_thread.start()

    movement_thread.start()

    # movement_thread.join()

except ExitCommand:
    logging.info("Landing due to collision")
    drone.land()

finally:

    controller.close()

    if drone.is_flying:
        logging.info("Landing normally")
        drone.land()

    # logging.info("Battery remaining %s", drone.get_battery())
    print(f"Battery: {drone.get_battery()}%")

    drone.end()


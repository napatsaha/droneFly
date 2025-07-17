"""
With real-time plots of state values
"""

import time, csv, os
import threading
import logging
import signal
from collections import deque

import numpy as np
# import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, animation
import matplotlib
# from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
from djitellopy import Tello

from analysis import aggregate, detector
from flight_control.collision import CollisionDetector

matplotlib.use("TkAgg")


class DataTracker:
    """
    Tracks plottable data gleaned from state queries during collision handling.
    """
    def __init__(self, metrics, max_size=100):
        self.metrics = metrics
        self.y_data = {}
        self.x_data = deque(maxlen=max_size)
        self.t0 = time.time()
        for met in metrics:
            self.y_data[met] = deque(maxlen=max_size)

    def start_timing(self):
        self.t0 = time.time()

    def add_data(self, dic: dict):
        for met in self.metrics:
            value = dic.get(met)
            self.y_data[met].append(value)
        self.x_data.append(time.time() - self.t0)

    def get_data(self):
        x = list(self.x_data)
        y = [self.y_data[met] for met in self.metrics]
        return x, y

class MainTimer:
    def __init__(self, duration):
        self.duration = duration

    def start(self):
        logging.info("Start timing")
        self.initial = time.time()

    def is_valid(self) -> bool:
        valid = time.time() - self.initial < self.duration
        return valid

    def get_time(self):
        return time.time() - self.initial


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

        data_tracker.add_data(state)

        collide = collision_detector(state)

        if collide:
            logging.info("Collided")
            break

        time.sleep(1/FPS)

    signal.raise_signal(signal.SIGTERM)
    logging.info("Terminating Collision Handling")


def frames():
    while not finished:
        time.sleep(1 / FPS)

        yield data_tracker.get_data()


def init_plot():
    data_tracker.start_timing()
    for ax, met in zip(axs, metrics):
        ax.set_title(met)
        ax.set_xlabel("sec")


def update_plot(args):
    # global l
    # print(args)
    xt, yts = args
    for line, yt, ax in zip(lines, yts, axs):
        line.set_data(xt, yt)
        if len(xt) > 1:
            ax.set_xlim(min(xt), max(xt))
        if len(yt) > 1:
            ax.set_ylim(min(yt), max(yt))
        # line, = ax.plot(xt, yt)
    return lines


FPS = 20
FLY_DURATION = 20
# FLIGHT_NAME = "Curved"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s -- %(threadName)s -- %(msg)s",
                    datefmt="%H:%M:%S")
signal.signal(signal.SIGTERM, signal_handler)
main_timer = MainTimer(duration=FLY_DURATION)

metrics = ["agx", "agy", "agz"]
aggregator = aggregate.MultiDiffAggregator(window=5, metrics=metrics)
peaker = detector.ZScorePeakDetection(window=20, threshold=5, influence=0.1)
collision_detector = CollisionDetector(aggregator, peaker)
collision_thread = threading.Thread(target=collision_handler, name="Collision")


data_tracker = DataTracker(metrics, max_size=120)

fig, axs = plt.subplots(1, len(metrics), figsize=(15, 7))
lines = [axis.plot([], [], '-')[0] for axis in axs]


drone = Tello()

drone.connect()

finished = False
anim = animation.FuncAnimation(fig, update_plot, frames=frames, cache_frame_data=False, interval=100, repeat=False,
                               init_func=init_plot)

try:
    logging.info("Taking Off")
    drone.takeoff()

    main_timer.start()
    collision_thread.start()

    logging.info("Sending Movement Command")
    drone.send_rc_control(-10, 0, 0, 0)

    plt.show()

    while main_timer.is_valid():
        time.sleep(1/FPS)

except ExitCommand:
    logging.info("Landing due to collision")
    drone.land()

finally:

    finished = True

    if drone.is_flying:
        logging.info("Landing normally")
        drone.land()

    # logging.info("Battery remaining %s", drone.get_battery())

    drone.end()


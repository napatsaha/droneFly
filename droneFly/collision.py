import threading
import logging
import time

from djitellopy import Tello

from droneFly import aggregate, detector
from droneFly.base import BaseWorker


class CollisionThread(BaseWorker):

    drone: Tello

    def __init__(self,
                 drone: Tello,
                 aggregator: aggregate.BaseAggregator,
                 peaker: detector.BaseDetector,
                 stopper: threading.Event, fps: int, **kwargs):
        super().__init__(stopper, fps, **kwargs)
        self.aggregator = aggregator
        self.peaker = peaker
        self.drone = drone

    def process(self, state_dict: dict):
        agg_value = self.aggregator(state_dict)
        has_collided = self.peaker(agg_value)
        if has_collided and not self.aggregator.separate:
            logging.info("Collision threshold reached: %.2f" % agg_value)
        return has_collided

    def _run(self):
        state = self.drone.get_current_state()

        collide = self.process(state)

        if collide:
            logging.info("Collided")
            self.terminate()

    def close(self):
        super().close()
        # logging.info("Setting Termination Event due to collision")


class CollisionDetector:
    def __init__(self,
                 aggregator: aggregate.BaseAggregator,
                 detect: detector.BaseDetector):
        self.aggregator = aggregator
        self.detector = detect

    def __call__(self, new_value):
        agg_value = self.aggregator(new_value)
        has_collided = self.detector(agg_value)
        if has_collided:
            print(agg_value)
        return has_collided


def collision_handler(event: threading.Event, collision_detector: CollisionDetector, drone: Tello, fps: int):
    # global drone, FPS, collision_detector

    logging.info("Beginning Collision Handling")

    while not event.is_set():
        state = drone.get_current_state()

        collide = collision_detector(state)

        if collide:
            logging.info("Collided")
            break

        time.sleep(1/fps)

    if not event.is_set():
        logging.info("Setting Termination Event due to collision")
        event.set()
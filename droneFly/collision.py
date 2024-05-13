import threading
import logging
import time

from djitellopy import Tello

from . import aggregate, detector


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
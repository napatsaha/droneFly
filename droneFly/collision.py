import threading
import logging, logging.config
import time

from djitellopy import Tello

from droneFly import aggregate, detect_peak
from droneFly.base import BaseWorker

logger = logging.getLogger(__name__)


class CollisionHandler(BaseWorker):

    drone: Tello

    def __init__(self,
                 drone: Tello,
                 aggregator: aggregate.BaseAggregator,
                 peaker: detect_peak.BasePeakDetector,
                 stopper: threading.Event, fps: int, **kwargs):
        super().__init__(stopper, fps, **kwargs)
        self.aggregator = aggregator
        self.peaker = peaker
        self.drone = drone
        self.logger = logger

    def process(self, state_dict: dict):
        agg_value = self.aggregator(state_dict)
        has_collided = self.peaker(agg_value)
        if has_collided and not self.aggregator.separate_output:
            logger.info("Collision threshold reached: %.2f" % agg_value)
        return has_collided

    def _run(self):
        state = self.drone.get_current_state()

        collide = self.process(state)

        if collide:
            logger.info("Collided")
            self.terminate()

    def close(self):
        super().close()
        # logging.info("Setting Termination Event due to collision")


# class CollisionDetector:
#     def __init__(self,
#                  aggregator: aggregate.BaseAggregator,
#                  detect: detect_peak.BasePeakDetector):
#         self.aggregator = aggregator
#         self.detector = detect
#
#     def __call__(self, new_value):
#         agg_value = self.aggregator(new_value)
#         has_collided = self.detector(agg_value)
#         if has_collided:
#             print(agg_value)
#         return has_collided
#
#
# def collision_handler(event: threading.Event, collision_detector: CollisionDetector, drone: Tello, fps: int):
#     # global drone, FPS, collision_detector
#
#     logging.info("Beginning Collision Handling")
#
#     while not event.is_set():
#         state = drone.get_current_state()
#
#         collide = collision_detector(state)
#
#         if collide:
#             logging.info("Collided")
#             break
#
#         time.sleep(1/fps)
#
#     if not event.is_set():
#         logging.info("Setting Termination Event due to collision")
#         event.set()
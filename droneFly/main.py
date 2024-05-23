"""
Main Program

Movement instructions control
using Event to terminate threads
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""

import threading
import logging, logging.config
import os

import yaml
from djitellopy import Tello

from droneFly import aggregate, detect_peak, collision, FLIGHT_PATH_DIR
# from droneFly.collision import CollisionDetector, collision_handler
from droneFly.flight import Controller
from droneFly.monitor import DataCollector


logger = logging.getLogger(__name__)


def main():
    # For debugging purposes only
    global collision_thread, movement_thread, terminate, drone, data_thread

    # Configurations
    FPS = 20
    MAX_WAIT = 30
    metric = ["agx", "agy", "agz"]
    flight_file = "move3.csv"
    agg_kwargs = dict(window=5)
    pk_kwargs = dict(window=20, threshold=10, influence=0.1)

    # Setup logging
    with open("./logging.yaml") as file:
        config = yaml.load(file, yaml.SafeLoader)
    logging.config.dictConfig(config)
    # logging.basicConfig(level=logging.INFO,
    #                     format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
    #                     datefmt="%H:%M:%S")

    # Instantiate Drone and Termination Event
    terminate = threading.Event()
    drone = Tello()

    # Collision Handler
    collision_thread = collision.CollisionHandler(
        drone=drone, fps=FPS, stopper=terminate,
        # aggregator=aggregate.MultiDiffAggregator(metrics=metric, separate_output=True, **agg_kwargs),
        aggregator=aggregate.NormAggregator(metrics=metric, **agg_kwargs),
        # peaker=detect_peak.MergedPeakDetector(
        #     detector_class=detect_peak.ZScorePeakDetection,
        #     metrics=metric,
        #     acceptance_rate='any',
        #     **pk_kwargs),
        peaker=detect_peak.ZScorePeakDetection(**pk_kwargs),
        name="Collision"
    )

    # collision_detector = CollisionDetector(
    #     aggregate.MultiDiffAggregator(metrics=metric, **agg_kwargs),
    #     detector.ZScorePeakDetection(**pk_kwargs)
    # )
    #
    # collision_thread = threading.Thread(target=collision_handler, name="Collision",
    #                                     kwargs=dict(
    #                                         drone=drone, fps=FPS,
    #                                         event=terminate,
    #                                         collision_detector=collision_detector
    #                                     ))

    data_thread = DataCollector(drone, terminate, FPS, name="CSV")

    # Movement Handler
    movement_thread = Controller(drone, os.path.join(FLIGHT_PATH_DIR, flight_file),
                                 fps=FPS, stopper=terminate, name="Movement")
    # movement_thread = threading.Thread(target=controller.run, name="Movement", args=(terminate,))

    # Establish connection
    drone.connect()

    try:
        logger.info("Taking Off")
        drone.takeoff()

        collision_thread.start()

        movement_thread.start()

        data_thread.start()

        # collision_thread.join()
        # movement_thread.join()
        terminate.wait(MAX_WAIT)

    finally:

        # Safety check if no MAX_WAIT runs out
        if not terminate.is_set():
            logger.info("Max wait time %2f sec reached" % MAX_WAIT)
            terminate.set()

        drone.send_rc_control(0,0,0,0)
        drone.land()

        # logging.info("Battery remaining %s", drone.get_battery())
        print(f"Battery: {drone.get_battery()}%")

        drone.end()


if __name__ == "__main__":
    main()

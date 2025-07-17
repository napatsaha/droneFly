"""
Main Program

Movement instructions control
using Event to terminate threads
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""
import datetime
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
    flight_file = "move0.csv"
    agg_kwargs = dict(window=5)
    pk_kwargs = dict(window=20, threshold=50, influence=0.1)

    # Setup logging
    logfilename = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f") + ".log"
    logfilename = os.path.join("../logs", logfilename)
    with open("./logging.yaml") as file:
        config = yaml.load(file, yaml.SafeLoader)
    config['handlers']['logfile']['filename'] = logfilename
    logging.config.dictConfig(config)
    # logging.basicConfig(level=logging.INFO,
    #                     format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
    #                     datefmt="%H:%M:%S")

    # Instantiate Drone and Termination Event
    terminate = threading.Event()  # Post take off until before landing
    finished = threading.Event()  # Activate before take, until after finish landing
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

    # Movement Handler
    movement_thread = Controller(drone, os.path.join(FLIGHT_PATH_DIR, flight_file),
                                 fps=FPS, stopper=terminate, name="Movement")
    # Data collector
    data_thread = DataCollector(drone, finished, FPS, name="CSV")

    # Establish connection
    logger.info("Establishing Connection...")
    drone.connect()

    data_thread.start()

    try:
        logger.info("Taking Off...")
        drone.takeoff()
        logger.info("Completed taking off procedure")

        collision_thread.start()

        movement_thread.start()


        # collision_thread.join()
        # movement_thread.join()
        terminate.wait(MAX_WAIT)

    finally:

        # Safety check if no MAX_WAIT runs out
        if not terminate.is_set():
            logger.info("Max wait time %.1f sec reached" % MAX_WAIT)
            terminate.set()

        drone.send_rc_control(0,0,0,0)
        logger.info("Initiating landing...")
        drone.land()
        logger.info("Successfully landed")

        finished.set()

        # logging.info("Battery remaining %s", drone.get_battery())
        logger.info(f"Battery Remaining: {drone.get_battery()}%")

        drone.end()


if __name__ == "__main__":
    main()

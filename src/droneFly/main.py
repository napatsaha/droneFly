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
import argparse

import yaml
from djitellopy import Tello

from droneFly import aggregate, detect_peak, collision, \
    FLIGHT_PATH_DIR, LOG_DIR, ROOT_DIR, RESULTS_DIR, CONFIG_DIR
# from droneFly.collision import CollisionDetector, collision_handler
from droneFly.flight import Controller
from droneFly.monitor import DataCollector


logger = logging.getLogger(__name__)


def main(config_file=None, save=True, flight_file=None):
    # For debugging purposes only
    global collision_thread, movement_thread, terminate, drone, data_thread

    # Configurations
    # FPS = 20
    # MAX_WAIT = 30
    # metric = ["agx", "agy", "agz"]
    # # flight_file = "move_forth-turn-forth.csv"
    # flight_file = "move_stationary.csv"
    # agg_kwargs = dict(window=5, metrics=metric)
    # pk_kwargs = dict(window=20, threshold=10, influence=0.1)
    # # Create config dictionary
    # exp_config = dict(
    #     fps=FPS,
    #     max_wait=MAX_WAIT,
    #     flight_file=flight_file,
    #     agg_cls="NormAggregator",
    #     agg_kwargs=agg_kwargs,
    #     pk_cls="ZScorePeakDetection",
    #     pk_kwargs=pk_kwargs,
    #     metric=metric
    # )
    # Read experiment configuration
    if config_file is None:
        config_file = "exp_config.yaml"
    with open(os.path.join(CONFIG_DIR, config_file), 'r') as file:
        exp_config = yaml.safe_load(file)
    FPS = exp_config["fps"]
    MAX_WAIT = exp_config["max_wait"]
    if flight_file is not None:
        flight_file = flight_file
        exp_config["flight_file"] = flight_file
    else:
        flight_file = exp_config.get("flight_file", "move_stationary.csv")

    # Setup parent directory to store all results
    now = datetime.datetime.now()
    date_dir = now.strftime("%Y-%m-%d")
    datetime_dir = now.strftime("%y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(RESULTS_DIR, date_dir, datetime_dir)

    if save and not os.path.exists(run_dir):
        os.makedirs(run_dir, exist_ok=True)

    # Setup logging
    # now = datetime.datetime.now()
    # date_dir = now.strftime("%Y-%m-%d")
    # logfilename = now.strftime("%y-%m-%d_%H-%M-%S-%f") + ".log"
    logfilename = os.path.join(run_dir, "events.log")
    # if not os.path.exists(os.path.join(LOG_DIR, date_dir)):
    #     os.makedirs(os.path.join(LOG_DIR, date_dir), exist_ok=True)
    
    # Reading logging config and update with log filename
    with open(os.path.join(ROOT_DIR, "logging.yaml")) as file:
        config = yaml.load(file, yaml.SafeLoader)
    if save:
        config['handlers']['logfile']['filename'] = logfilename
    else:
        config["handlers"].pop("logfile", None)  # Remove file handler if not saving
        for d in config["loggers"].values():
            print(d)
            d["handlers"] = ["console"]  # Use only console handler
    logging.config.dictConfig(config)
    # logging.basicConfig(level=logging.INFO,
    #                     format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
    #                     datefmt="%H:%M:%S")

    # Save experiment configuration
    exp_config_path = os.path.join(run_dir, "experiment_config.yaml")
    if save:
        with open(exp_config_path, 'w') as file:
            yaml.safe_dump(exp_config, file, sort_keys=False)

    # Instantiate Drone and Termination Event
    terminate = threading.Event()  # Post take off until before landing
    finished = threading.Event()  # Activate before take, until after finish landing
    drone = Tello()

    # Collision Handler
    collision_thread = collision.CollisionHandler(
        drone=drone, fps=FPS, stopper=terminate,
        # aggregator=aggregate.MultiDiffAggregator(metrics=metric, separate_output=True, **agg_kwargs),
        # aggregator=aggregate.NormAggregator(metrics=metric, **agg_kwargs),
        aggregator=getattr(aggregate, exp_config["agg_cls"])(**exp_config["agg_kwargs"]),
        # peaker=detect_peak.MergedPeakDetector(
        #     detector_class=detect_peak.ZScorePeakDetection,
        #     metrics=metric,
        #     acceptance_rate='any',
        #     **pk_kwargs),
        peaker=getattr(detect_peak, exp_config["pk_cls"])(**exp_config["pk_kwargs"]),
        # peaker=detect_peak.ZScorePeakDetection(**pk_kwargs),
        name="Collision"
    )

    # Movement Handler
    movement_thread = Controller(drone, os.path.join(FLIGHT_PATH_DIR, flight_file),
                                 fps=FPS, stopper=terminate, name="Movement")
    # Data collector
    if save:
        data_thread = DataCollector(drone, stopper=finished, fps=FPS, name="CSV", file_path=run_dir)

    # Establish connection
    logger.info("Establishing Connection...")
    drone.connect()

    if save:
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
    parser = argparse.ArgumentParser(description="Drone Flight Control Program")
    parser.add_argument("--config", "-c", type=str, default="exp_config.yaml",
                        help="Path to the experiment configuration file")
    parser.add_argument("--dont-save", "-d", action="store_true",
                        help="Prevent saving results to a directory")
    parser.add_argument("--flight-file", "-f", type=str, default="move_stationary.csv",
                        help="Path to the flight trajectory file within the flight path directory")
    args = parser.parse_args()
    print(f"config file: {args.config}, save: {not args.dont_save}")
    main(config_file=args.config, save=not args.dont_save, flight_file=args.flight_file)

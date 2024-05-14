"""
New module

Movement instructions control
using Event to terminate threads
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""

import threading
import logging
import os

from djitellopy import Tello

from droneFly import aggregate, detector, collision, FLIGHT_PATH_DIR
# from droneFly.collision import CollisionDetector, collision_handler
from droneFly.movement import Controller


def main():
    global collision_thread, movement_thread, terminate, drone

    # Configurations
    FPS = 20
    MAX_WAIT = 30
    metric = ["agx", "agy", "agz"]
    flight_file = "move3.csv"
    agg_kwargs = dict(window=5)
    pk_kwargs = dict(window=20, threshold=10, influence=0.1)

    # Setup logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
                        datefmt="%H:%M:%S")

    # Instantiate Drone and Termination Event
    terminate = threading.Event()
    drone = Tello()

    # Collision Handler
    collision_thread = collision.CollisionThread(
        drone=drone, fps=FPS, stopper=terminate,
        aggregator=aggregate.MultiDiffAggregator(metrics=metric, **agg_kwargs),
        peaker=detector.ZScorePeakDetection(**pk_kwargs),
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

    # Movement Handler
    movement_thread = Controller(drone, os.path.join(FLIGHT_PATH_DIR, flight_file),
                                 fps=FPS, stopper=terminate, name="Movement")
    # movement_thread = threading.Thread(target=controller.run, name="Movement", args=(terminate,))

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

        # for thread in threading.enumerate():
        #     thread.is

        drone.send_rc_control(0,0,0,0)
        drone.land()

        # logging.info("Battery remaining %s", drone.get_battery())
        print(f"Battery: {drone.get_battery()}%")

        drone.end()


if __name__ == "__main__":
    main()

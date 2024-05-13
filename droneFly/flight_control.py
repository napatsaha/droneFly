"""
New module

Movement instructions control
using Event to terminate threads
Zscore-based windowed-Jerk-sum xyz acceleration as signal to detect collision
"""

import threading
import logging
import signal

from djitellopy import Tello

from . import aggregate, detector
from .collision import CollisionDetector, collision_handler
from .movement import Controller


def main():

    # Configurations
    FPS = 20
    MAX_WAIT = 30
    metric = ["agx", "agy", "agz"]

    # Setup logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(threadName)-10s] -- %(msg)s",
                        datefmt="%H:%M:%S")

    # Instantiate Drone and Termination Event
    terminate = threading.Event()
    drone = Tello()

    # Collision Handler
    collision_detector = CollisionDetector(
        aggregate.MultiDiffAggregator(window=5, metrics=metric),
        detector.ZScorePeakDetection(window=20, threshold=15, influence=0.1)
    )

    collision_thread = threading.Thread(target=collision_handler, name="Collision",
                                        kwargs=dict(
                                            drone=drone, fps=FPS,
                                            event=terminate,
                                            collision_detector=collision_detector
                                        ))

    # Movement Handler
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


if __name__ == "__main__":
    main()

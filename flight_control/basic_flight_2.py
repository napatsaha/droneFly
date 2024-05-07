import time, csv, os
import threading
from djitellopy import Tello

from analysis.aggregate import MultiDiffAggregator
from analysis.detector import ZScorePeakDetection
from collision import SingleMetricDiffDetector


def collision_handler():
    global drone, FPS

    metric = ["agx", "agy", "agz"]
    aggregator = MultiDiffAggregator(window=5, metrics=metric)
    detector = ZScorePeakDetection(window=20, threshold=5, influence=0.1)

    while True:
        state = drone.get_current_state()

        signal = aggregator(state)
        collide = detector.add(signal)

        if collide:
            print("Collided")
            break

        time.sleep(1/FPS)

    print("Landing due to collision")
    drone.land()


FPS = 20
FLY_DURATION = 5
# FLIGHT_NAME = "Curved"

drone = Tello()

drone.connect()

collision_thread = threading.Thread(target=collision_handler)

# drone.send_rc_control(0, 30, 0, 0)


try:
    drone.takeoff()

    # t0 = time.time()

    collision_thread.start()

    drone.send_rc_control(0, 10, 0, 0)

    time.sleep(FLY_DURATION)


finally:

    # drone.send_rc_control(0, 0, 0, 0)

    if drone.is_flying:
        print("Landing normally")
        drone.land()

    drone.end()


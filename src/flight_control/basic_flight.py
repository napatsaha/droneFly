import time, csv, os
from djitellopy import Tello
from collision import SingleMetricDiffDetector

FPS = 20
FLY_DURATION = 10
# FLIGHT_NAME = "Curved"

drone = Tello()
detector = SingleMetricDiffDetector("agz", 200)

drone.connect()


state = drone.get_current_state()

drone.send_rc_control(0, 30, 0, 0)
drone.takeoff()

t0 = time.time()



try:

    time_elapsed = time.time() - t0
    while time_elapsed < FLY_DURATION:
        state = drone.get_current_state()
        collide = detector.update(state)
        print(state["tof"])
        if collide:
            print(detector.records)
            print("COLLIDE")
            drone.send_rc_control(0, -30, 0, 0)
            break
        time.sleep(1/FPS)
        time_elapsed = time.time() - t0

finally:

    # drone.send_rc_control(0, 0, 0, 0)

    drone.land()

    drone.end()


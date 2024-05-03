import time, csv, os
from djitellopy import Tello

FPS = 20
FLY_DURATION = 5
FLIGHT_NAME = "Blocked"
DIR_NAME = "../data"

if not os.path.exists(DIR_NAME):
    os.mkdir(DIR_NAME)


drone = Tello()

drone.connect()


state = drone.get_current_state()

filename = FLIGHT_NAME + "_" + time.strftime("%y-%m-%d_%H-%M-%S") + ".csv"
filename = os.path.join("../data", filename)
csvfile = open(filename, 'w', newline='')

writer = csv.DictWriter(csvfile, fieldnames=['time_elapsed'] + list(state.keys()))
writer.writeheader()

drone.takeoff()

t0 = time.time()



try:
    drone.send_rc_control(0, 20, 0, 45)
    time_elapsed = time.time() - t0
    while time_elapsed < FLY_DURATION:
        state = drone.get_current_state()
        state['time_elapsed'] = f"{time_elapsed:.3f}"
        writer.writerow(state)
        time.sleep(1/FPS)
        time_elapsed = time.time() - t0

finally:
    csvfile.close()
    print(f"Record saved to {filename}")

    drone.send_rc_control(0, 0, 0, 0)

    drone.land()

    drone.end()


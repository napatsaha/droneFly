import time, csv
from djitellopy import Tello

FPS = 10


drone = Tello()

drone.connect()

drone.set_speed(10)

print(time.strftime("%H:%M:%S"), "\t", "Taking off")
drone.takeoff()

try:
    print(time.strftime("%H:%M:%S"), "\t", "Moving forward 50 cm")
    drone.move_forward(50)
    print(time.strftime("%H:%M:%S"), "\t", "Rotating 90 deg")
    drone.rotate_clockwise(90)
    print(time.strftime("%H:%M:%S"), "\t", "Moving forward 50 cm")
    drone.move_forward(50)

finally:
    # drone.send_command_without_return("close")

# drone.send_rc_control(0, 30, 0, 60)
# time.sleep(5)
# drone.send_rc_control(0, -20, 0, -60)
# time.sleep(2)
    print(time.strftime("%H:%M:%S"), "\t", "Stopping all motion")
    drone.send_rc_control(0, 0, 0, 0)

    print(time.strftime("%H:%M:%S"), "\t", "Landing")
    drone.land()

print(drone.get_battery())
drone.end()


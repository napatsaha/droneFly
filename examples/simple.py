import time

from djitellopy import Tello

tello = Tello()

tello.connect()
tello.takeoff()

tello.send_rc_control(0, 0, 0, 60)
time.sleep(1.5)
tello.send_rc_control(0, 0, 0, -60)
time.sleep(1.5)


tello.land()
tello.end()

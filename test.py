import pygame

import djitellopy
import socket

drone = djitellopy.tello.Tello()

drone.connect()
state = drone.get_current_state()
print(state)

drone.set_speed(10)
drone.takeoff()

for _ in range(4):
    drone.move_forward(20)
    drone.rotate_clockwise(90)
    print(drone.get_current_state())

drone.land()
drone.end()

drone.emergency()
from djitellopy import Tello
import time

tello = Tello()
tello.connect()
tello.send_command_with_return("command")
time.sleep(1)

tello.takeoff()
time.sleep(2)

print("Reading velocities for 5 seconds...")
for i in range(50):
    vx = tello.get_speed_x()
    vy = tello.get_speed_y()
    print(f"vx: {vx}, vy: {vy}")
    time.sleep(0.1)

tello.land()
tello.end()
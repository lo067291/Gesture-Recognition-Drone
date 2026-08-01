from djitellopy import Tello
import time

tello = Tello()
tello.connect()
#establish battery connection
battery = tello.get_battery()
print(f"Battery: {battery}%")

# Force SDK mode, enables percise movements
tello.send_command_with_return("command")
time.sleep(1)

print("Taking off")
tello.takeoff()
time.sleep(2)#hover for 2 seconds in the air after rising

#this will make sure the drone rises the exact height everytime
current_height = tello.get_height()
print(f"Current height: {current_height} cm")

target_height = 60
difference = target_height - current_height

if difference >= 20:
    tello.move_up(difference)
elif difference <= -20:
    tello.move_down(abs(difference))
else:
    print("Height is close enough, no need to move")

print(f"Adjusted to {target_height} cm")

time.sleep(2)#hover for 2 seconds



#Now begin testing directional capabilities
print("Testing directional movements")
print("Moving foward")
tello.move_forward(20)
time.sleep(1)
print("Moving backward")
tello.move_back(20)
time.sleep(1)
print("Moving left")
tello.move_left(20)
time.sleep(1)
print("Moving right")
tello.move_right(20)
time.sleep(1)
print("Turning")
tello.rotate_clockwise(90)
time.sleep(1)
print("Turning back")
tello.rotate_counter_clockwise(90)
time.sleep(1)

print("Landing")
tello.land()#calls land and will land in general area (not specific coordinates yet)

tello.end()#needed to end the connection
print("✅ Flight complete!")

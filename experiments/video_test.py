from djitellopy import Tello
import cv2
import time

# Connect to drone
tello = Tello()
tello.connect()
tello.send_command_with_return("command")
time.sleep(1)

battery = tello.get_battery()
print(f"Battery: {battery}%")

# Start video stream (drone stays on ground)
tello.streamon()
time.sleep(2)

frame_reader = tello.get_frame_read()
print("Video stream started - press Q to quit")

while True:
    # Get current frame from drone camera
    frame = frame_reader.frame

    # Display frame
    cv2.imshow("Tello Camera Feed", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup, safely close everything running
tello.streamoff()
tello.end()
cv2.destroyAllWindows()
print("Stream closed")
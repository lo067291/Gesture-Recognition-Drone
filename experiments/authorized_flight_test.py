from djitellopy import Tello
import cv2
import face_recognition
import time

# Load owner's face
print("Loading owner face...")
owner_image = face_recognition.load_image_file("owner_resized.jpg")
owner_encoding = face_recognition.face_encodings(owner_image)[0]
print("Owner face loaded successfully!")

# Connect to drone
tello = Tello()
tello.connect()
tello.send_command_with_return("command")
time.sleep(1)

battery = tello.get_battery()
print(f"Battery: {battery}%")

# Takeoff
print("Taking off...")
tello.takeoff()
time.sleep(2)

# Start video stream
tello.streamon()
time.sleep(2)
frame_reader = tello.get_frame_read()

# Authentication phase
print("Scanning for owner face...")
timeout_seconds = 10
start_time = time.time()
authorized = False

while time.time() - start_time < timeout_seconds:
    frame = frame_reader.frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([owner_encoding], face_encoding)
        if matches[0]:
            authorized = True
            print("✅ OWNER CONFIRMED!")
            break

    cv2.imshow("Tello Auth Check", frame)
    cv2.waitKey(1)

    if authorized:
        break

# Decision based on authentication result
if authorized:
    print("Access granted - hovering in authorized mode")
    time.sleep(3)  # placeholder for gesture mode (Week 3)
else:
    print("❌ No owner detected - rejection sequence")
    tello.rotate_clockwise(360)
    time.sleep(2)

print("Landing...")
tello.land()

tello.streamoff()
tello.end()
cv2.destroyAllWindows()
print("Flight complete!")
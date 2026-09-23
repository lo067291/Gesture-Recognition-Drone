from djitellopy import Tello
import cv2
import face_recognition
import time

# Load owner's face and encode it
print("Loading owner face")
owner_image = face_recognition.load_image_file("owner_resized.jpg")
owner_encoding = face_recognition.face_encodings(owner_image)[0]
print("Owner face loaded successfully!")

# Connect to drone and read battery
tello = Tello()
tello.connect()
tello.send_command_with_return("command")
time.sleep(1)
battery = tello.get_battery()
print(f"Battery: {battery}%")

# Start video stream
tello.streamon()
time.sleep(2)
frame_reader = tello.get_frame_read()

print("Scanning for owner face")

while True:
    frame = frame_reader.frame
    #Convert OpenCV frame to RGB frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Find face in current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for(top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        #Now compare the shown face to the "owner" face
        matches = face_recognition.compare_faces([owner_encoding], face_encoding)
        if matches[0]:
            label = "Owner - Authorized"
            color = (0, 255, 0)#standarg green rbg color
        else:
            label = "Unknown"
            color = (0, 0, 255)#standard rgb color
        #Label bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, bottom - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Tello Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#End video stream
tello.streamoff()
tello.end()
cv2.destroyAllWindows()
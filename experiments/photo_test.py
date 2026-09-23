import face_recognition
import cv2

# Load and resize the image
img = cv2.imread("owner.jpeg")
print(f"Original shape: {img.shape}")

# Resize to a reasonable width (800px) while keeping aspect ratio
height, width = img.shape[:2]
scale = 800 / width
new_width = 800
new_height = int(height * scale)
resized_img = cv2.resize(img, (new_width, new_height))

# Save the resized version
cv2.imwrite("owner_resized.jpg", resized_img)
print(f"Resized shape: {resized_img.shape}")

# Now try face detection on the resized image
owner_image = face_recognition.load_image_file("owner_resized.jpg")
face_locations = face_recognition.face_locations(owner_image)
print(f"Faces found: {len(face_locations)}")

if len(face_locations) > 0:
    encoding = face_recognition.face_encodings(owner_image, face_locations)[0]
    print("✅ Face encoding successful!")
else:
    print("❌ Still no face detected - check the image manually")
    cv2.imshow("Resized Image", resized_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
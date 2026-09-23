import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

def is_fingers_crossed(hand_landmarks):
    #landmark indices: 8 and 12, index fingertip and middle fingertip
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    index_base = hand_landmarks.landmark[5]#base posistions for index and middle fingers
    middle_base = hand_landmarks.landmark[9]

    #if index tip is < middle tip means fingers crossed
    #or if index tip is greater than middle tip the order flips
    normal_order = index_tip.x < middle_base.x
    tip_order = index_tip.x < middle_tip.x

    return normal_order != tip_order

while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture_text = "No hand detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_fingers_crossed(hand_landmarks):
                gesture_text = "FINGERS CROSSED - Finger Follow Mode"
            else:
                gesture_text = "Normal hand position"

    cv2.putText(frame, gesture_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Gesture Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
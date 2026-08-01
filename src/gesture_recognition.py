import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

def distance_3d(p1, p2): #made this because the model had trobule recognizing hand when turned
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def finger_is_up(lm, tip_id, pip_id):
    wrist = lm.landmark[0]
    tip = lm.landmark[tip_id]
    pip = lm.landmark[pip_id]

    tip_dist = distance_3d(tip, wrist)
    pip_dist = distance_3d(pip, wrist)

    # If tip is farther from wrist than the pip joint, finger is extended
    return tip_dist > pip_dist


def is_fingers_crossed(lm):
    index_up = finger_is_up(lm, 8, 6)
    middle_up = finger_is_up(lm, 12, 10)
    
    if not(index_up and middle_up):
        return False#not allowed to be crossed unless both fingers are extended
    
    index_tip, middlle_tip = lm.landmark[8], lm.landmark[12]
    index_base, middle_base = lm.landmark[5], lm.landmark[9]
    normal_order = index_tip.x < middle_base.x
    tip_order = index_tip.x < middlle_tip.x
    
    return normal_order != tip_order


def is_open_palm(lm):
    return (finger_is_up(lm, 8, 6) and
            finger_is_up(lm, 12, 10) and
            finger_is_up(lm, 16, 14) and
            finger_is_up(lm, 20, 18))


def is_closed_fist(lm):
    return (not finger_is_up(lm, 8, 6) and
            not finger_is_up(lm, 12, 10) and
            not finger_is_up(lm, 16, 14) and
            not finger_is_up(lm, 20, 18))


def is_pointing_direction(lm): #changed from checking strict location to checking location relative to hand orientation
    index_up = finger_is_up(lm, 8, 6)
    others_down = (not finger_is_up(lm, 12, 10) and
                   not finger_is_up(lm, 16, 14) and
                   not finger_is_up(lm, 20, 18))

    if not (index_up and others_down):
        return None

    wrist = lm.landmark[0]
    index_tip = lm.landmark[8]
    index_base = lm.landmark[5]

    #vector from wrist to index base defines the hands axis for orientation
    hand_dir_x = index_base.x - wrist.x
    hand_dir_y = index_base.y - wrist.y

    #vector from index base to index tip defines the actual direction of the hand pointing
    point_dir_x = index_tip.x - index_base.x
    point_dir_y = index_tip.y - index_base.y

    #perpendicualr vector to hand_dir, defines hands "right side"
    #flips automatically based on which way the palm is facing
    perp_x = -hand_dir_y
    perp_y = hand_dir_x

    # Project point_dir onto perp vector to determine left/right relative to palm orientation
    left_right_component = (point_dir_x * perp_x) + (point_dir_y * perp_y)
    up_down_component = (point_dir_x * hand_dir_x) + (point_dir_y * hand_dir_y)

    if abs(up_down_component) > abs(left_right_component):
        return "up" if up_down_component < 0 else "down"
    else:
        return "left" if left_right_component < 0 else "right"

def is_thumbs_up(lm):
    wrist = lm.landmark[0]
    thumb_tip, thumb_ip = lm.landmark[4], lm.landmark[3]
    thumb_extended = distance_3d(thumb_tip, wrist) > distance_3d(thumb_ip, wrist)

    others_down = (not finger_is_up(lm, 8, 6) and
                   not finger_is_up(lm, 12, 10) and
                   not finger_is_up(lm, 16, 14) and
                   not finger_is_up(lm, 20, 18))

    # Thumb tip y should be above the wrist y for "up" orientation
    thumb_points_up = thumb_tip.y < wrist.y

    return thumb_extended and others_down and thumb_points_up


def is_thumbs_down(lm):
    wrist = lm.landmark[0]
    thumb_tip, thumb_ip = lm.landmark[4], lm.landmark[3]
    thumb_extended = distance_3d(thumb_tip, wrist) > distance_3d(thumb_ip, wrist)

    others_down = (not finger_is_up(lm, 8, 6) and
                   not finger_is_up(lm, 12, 10) and
                   not finger_is_up(lm, 16, 14) and
                   not finger_is_up(lm, 20, 18))

    thumb_points_down = thumb_tip.y > wrist.y

    return thumb_extended and others_down and thumb_points_down


def classify_gesture(lm):
    if is_fingers_crossed(lm):
        return "FINGERS CROSSED - Finger Follow Mode"
    elif is_closed_fist(lm):
        return "CLOSED FIST - Land/Return Home"
    elif is_open_palm(lm):
        return "OPEN PALM - Hover/Stop"

    pointing_dir = is_pointing_direction(lm)
    if pointing_dir == "up":
        return "POINTING UP - Ascend"
    elif pointing_dir == "down":
        return "POINTING DOWN - Descend"
    elif pointing_dir == "left":
        return "POINTING LEFT - Move Left"
    elif pointing_dir == "right":
        return "POINTING RIGHT - Move Right"

    if is_thumbs_up(lm):
        return "THUMBS UP - Move Forward"
    elif is_thumbs_down(lm):
        return "THUMBS DOWN - Move Backward"

    return "Unclassified hand position"


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
            gesture_text = classify_gesture(hand_landmarks)

    cv2.putText(frame, gesture_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Hand Gesture Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

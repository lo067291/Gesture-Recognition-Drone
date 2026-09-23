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

def get_pointing_components(lm):
    index_up = finger_is_up(lm, 8, 6)
    others_down = (not finger_is_up(lm, 12, 10) and
                   not finger_is_up(lm, 16, 14) and
                   not finger_is_up(lm, 20, 18))

    if not (index_up and others_down):
        return None, None, None

    wrist = lm.landmark[0]
    index_tip = lm.landmark[8]
    index_base = lm.landmark[5]

    hand_dir_x = index_base.x - wrist.x
    hand_dir_y = index_base.y - wrist.y

    point_dir_x = index_tip.x - index_base.x
    point_dir_y = index_tip.y - index_base.y

    perp_x = -hand_dir_y
    perp_y = hand_dir_x

    left_right_component = (point_dir_x * perp_x) + (point_dir_y * perp_y)
    up_down_component = (point_dir_x * hand_dir_x) + (point_dir_y * hand_dir_y)

    angle = math.atan2(left_right_component, up_down_component)
    angle_degrees = math.degrees(angle)

    return left_right_component, up_down_component, angle_degrees

def is_pointing_direction(lm):
    index_up = finger_is_up(lm, 8, 6)
    others_down = (not finger_is_up(lm, 12, 10) and
                   not finger_is_up(lm, 16, 14) and
                   not finger_is_up(lm, 20, 18))

    if not (index_up and others_down):
        return None

    # Use middle finger base (9) as stable palm reference instead of wrist
    palm_ref = lm.landmark[9]
    index_tip = lm.landmark[8]
    index_base = lm.landmark[5]

    # 3D vector from palm reference to index base - stable "hand up" axis
    hand_dir_x = index_base.x - palm_ref.x
    hand_dir_y = index_base.y - palm_ref.y
    hand_dir_z = index_base.z - palm_ref.z

    # 3D vector for actual pointing direction
    point_dir_x = index_tip.x - index_base.x
    point_dir_y = index_tip.y - index_base.y
    point_dir_z = index_tip.z - index_base.z

    # Use the y and z components specifically for up/down detection,
    # since bending the wrist forward primarily changes depth (z)
    # and vertical (y) position, not left/right (x)
    up_down_component = (point_dir_y * hand_dir_y) + (point_dir_z * hand_dir_z)

    # Left/right still uses the perpendicular-in-xy-plane approach,
    # since horizontal pointing doesn't involve wrist flexion
    perp_x = -hand_dir_y
    perp_y = hand_dir_x
    left_right_component = (point_dir_x * perp_x) + (point_dir_y * perp_y)

    angle = math.atan2(left_right_component, up_down_component)
    angle_degrees = math.degrees(angle)

    if -45 <= angle_degrees < 45:
        return "up"
    elif 45 <= angle_degrees < 135:
        return "right"
    elif -135 <= angle_degrees < -45:
        return "left"
    else:
        return "down"

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

def debug_index_state(lm):
    wrist = lm.landmark[0]
    tip = lm.landmark[8]
    pip = lm.landmark[6]
    tip_dist = distance_3d(tip, wrist)
    pip_dist = distance_3d(pip, wrist)
    return tip_dist, pip_dist, tip_dist > pip_dist

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

            tip_dist, pip_dist, index_extended = debug_index_state(hand_landmarks)

            cv2.putText(frame, f"tip_dist: {tip_dist:.4f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"pip_dist: {pip_dist:.4f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"index_extended: {index_extended}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Debug Values", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

cap.release()
cv2.destroyAllWindows()
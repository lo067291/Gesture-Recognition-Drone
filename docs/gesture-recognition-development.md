## Gesture Recognition: Development Process

**Status: active debugging.** Gesture classification is still being refined, and the webcam prototype is not integrated with drone flight. These notes describe approaches explored so far; they do not establish reliable classification across all hand orientations.

### Attempt 1: Basic Finger Curl Detection (2D)

Initial approach compared each fingertip's y-coordinate directly 
against its PIP joint's y-coordinate:

```python
def finger_is_up(lm, tip_id, pip_id):
    return lm.landmark[tip_id].y < lm.landmark[pip_id].y
```

**Result:** Worked correctly when the palm faced the camera directly.

**Problem discovered:** Gestures failed entirely when the camera saw 
the back of the hand instead of the palm. Rotating the hand changed 
how fingers projected onto the 2D image plane, breaking the simple 
y-coordinate comparison even though the physical finger position 
hadn't changed.

**Root cause:** MediaPipe's (x, y) landmarks are a 2D projection of 
a 3D hand. The same physical gesture produces different 2D 
coordinates depending on hand orientation relative to the camera.

---

### Attempt 2: 3D Distance-Based Finger Curl Detection

Reworked finger curl detection using MediaPipe's z-coordinate (depth) 
in addition to x and y, computing a distance heuristic from each 
fingertip to the wrist:

```python
def distance_3d(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2 +
        (p1.z - p2.z) ** 2
    )

def finger_is_up(lm, tip_id, pip_id):
    wrist = lm.landmark[0]
    tip_dist = distance_3d(lm.landmark[tip_id], wrist)
    pip_dist = distance_3d(lm.landmark[pip_id], wrist)
    return tip_dist > pip_dist
```

**Current assessment:** The prototype uses landmark-distance comparisons to estimate finger extension. Classification still requires debugging and validation across hand poses and orientations; these comparisons do not guarantee correct recognition.

---

### Attempt 3: Pointing Direction - First Try (Failed)

Directional pointing (left/right/up/down) initially used raw 2D 
displacement between the index fingertip and its base:

```python
dx = index_tip.x - index_base.x
dy = index_tip.y - index_base.y

if abs(dy) > abs(dx):
    return "up" if dy < 0 else "down"
else:
    return "right" if dx > 0 else "left"
```

**Result:** Worked correctly for pointing up/down, and for left/right 
only when the palm faced the camera.

**Problem discovered:** When pointing normally (palm facing the 
user, back of hand facing the camera - the natural way people 
point), left and right were reversed. Rotating the hand 180° around 
its long axis flips which way "left" and "right" appear in the 
camera's fixed image frame, even though the physical pointing 
direction relative to the person hadn't changed.

**Root cause:** This was the same underlying issue as Attempt 1 - 
measuring direction in the camera's coordinate frame instead of the 
hand's own coordinate frame. Unlike finger curl (fixed with 3D 
distance), directional left/right needed an actual reference frame 
tied to the hand's orientation, not just a depth value.

---

### Attempt 4: Hand-Relative Coordinate Frame (Earlier Approach)

Built a local coordinate system from the hand's own landmarks, then 
measured pointing direction relative to that frame instead of the 
camera's fixed axes:

```python
def is_pointing_direction(lm):
    wrist = lm.landmark[0]
    index_tip = lm.landmark[8]
    index_base = lm.landmark[5]

    # Hand's own "up" axis: wrist -> index base
    hand_dir_x = index_base.x - wrist.x
    hand_dir_y = index_base.y - wrist.y

    # Actual pointing direction: index base -> index tip
    point_dir_x = index_tip.x - index_base.x
    point_dir_y = index_tip.y - index_base.y

    # Perpendicular vector (90 deg rotation) - hand's own "right" axis
    perp_x = -hand_dir_y
    perp_y = hand_dir_x

    # Dot products project pointing direction onto each hand-relative axis
    left_right_component = (point_dir_x * perp_x) + (point_dir_y * perp_y)
    up_down_component = (point_dir_x * hand_dir_x) + (point_dir_y * hand_dir_y)

    if abs(up_down_component) > abs(left_right_component):
        return "up" if up_down_component < 0 else "down"
    else:
        return "left" if left_right_component < 0 else "right"
```

**Key insight:** Instead of asking "did the fingertip move left/right 
in the camera's frame," the question became "did the fingertip move 
left/right relative to the hand's own orientation." This required:

1. Building a vector from the wrist to the index base, which always 
   points "up" along the hand itself, regardless of camera-relative 
   rotation
2. Rotating that vector 90 degrees (using the 2D rotation identity 
   `(x, y) -> (-y, x)`) to get a "right" axis that automatically 
   rotates with the hand
3. Using the dot product to project the actual pointing vector onto 
   each of these hand-relative axes, determining how much of the 
   gesture lies along "hand-up" vs. "hand-right"

**Current assessment:** The hand-relative projection approach is implemented, but pointing-direction classification is still being debugged. Robustness across palm orientation, hand rotation, and ambiguous poses remains to be validated.

---

### Current Uploaded Revision: Palm-Reference Projection and Angle Sectors

The uploaded `normal_finger_detection.py`, now stored as [../src/gesture_recognition.py](../src/gesture_recognition.py), contains a later version of `is_pointing_direction()`:

1. Use middle-finger base (landmark 9) as `palm_ref`.
2. Build a reference vector from that point to index-finger base (5).
3. Build a pointing vector from index-finger base (5) to tip (8).
4. Compute an up/down component from the y/z terms and a left/right component using the perpendicular reference in the x/y plane.
5. Use `atan2(left_right_component, up_down_component)` and 90-degree sectors to assign a direction.

The code retains the earlier wrist-based `get_pointing_components()` helper. That helper and the revised classifier use different calculations. The active webcam loop currently shows finger-distance debug values and does not call `classify_gesture()`; this intentionally preserves the uploaded debugging configuration.

The projection revision is being debugged and is not claimed to provide a fully validated 3D coordinate transform.

### Current Takeaways

Coordinate-frame choices and landmark geometry are central to the approaches explored here. The prototype combines x/y/z landmark-distance heuristics for finger extension with 2D hand-relative projections for pointing direction.

These are working hypotheses and implementation approaches, not a completed solution. Current work focuses on accurate gesture classification before connecting the classifier to drone flight. Threading and PID finger-following have not been started, and return-to-launch remains unfinished.

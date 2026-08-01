## Gesture Recognition: Development Process

This section documents the iterative debugging process behind the 
gesture classification system, since the final solution required 
solving real coordinate-frame problems rather than just tuning 
thresholds.

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
in addition to x and y, measuring true 3D distance from each 
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

**Result:** Open palm, closed fist, thumbs up/down, and fingers 
crossed now classify correctly regardless of hand orientation, since 
an extended finger is always farther from the wrist in true 3D 
space - not just in a flattened camera projection.

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

### Attempt 4: Hand-Relative Coordinate Frame (Final Solution)

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

**Result:** Pointing direction now classifies correctly regardless 
of whether the palm faces the camera or faces the user - the code 
determines direction relative to the hand's own orientation rather 
than the camera's fixed image frame.

---

### Summary of Root Cause Across All Attempts

Every failure mode traced back to the same underlying issue: 
**measuring hand geometry using the camera's fixed 2D image frame 
instead of a frame relative to the hand itself.** Finger curl was 
solved by adding a third dimension (z-depth). Pointing direction 
required building an entirely new 2D coordinate frame from the 
hand's own landmarks and using vector projection (dot products) to 
measure direction within that frame - the same general technique 
used in robotics for transforming between a sensor's frame and a 
robot's local reference frame.

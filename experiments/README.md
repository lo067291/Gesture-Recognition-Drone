# Development Experiments

These scripts preserve the uploaded PyCharm development steps. Overlap is intentional: each script isolates a component or records an earlier experiment. The current gesture implementation is [../src/gesture_recognition.py](../src/gesture_recognition.py).

## Source Mapping

| Original PyCharm file | Repository file | Role |
|---|---|---|
| normal_finger_detection.py | [../src/gesture_recognition.py](../src/gesture_recognition.py) | Latest gesture/vector-projection source in the upload; debug display is active |
| drone_test.py | [../src/drone_control.py](../src/drone_control.py) | Standalone movement test |
| face_auth_test.py | [../src/face_auth.py](../src/face_auth.py) | Face matching over drone video; no takeoff |
| authorized_flight_test.py | [authorized_flight_test.py](authorized_flight_test.py) | Takeoff, timed face check, authorized hover or rejection rotation, landing |
| fingers_crossed_test.py | [fingers_crossed_test.py](fingers_crossed_test.py) | Isolated crossed-finger detection |
| gesture_test.py | [gesture_test.py](gesture_test.py) | Webcam hand-tracking and landmark display |
| hand-test.py | [hand_test.py](hand_test.py) | Separate hand-tracking experiment |
| photo test.py | [photo_test.py](photo_test.py) | Resize owner.jpeg and check face detection; writes owner_resized.jpg |
| pid_test_file.py | [pid_test_file.py](pid_test_file.py) | Takeoff and velocity-telemetry sampling; does not implement PID |
| video_test.py | [video_test.py](video_test.py) | Ground-based drone-video test |

The archive records `normal_finger_detection.py` as modified on August 23, 2026, later than the other included scripts. Its revised `is_pointing_direction()` uses landmark 9 as the palm reference, combines y/z and x/y projection components, and uses `atan2` to select an angle sector. The earlier wrist-based `get_pointing_components()` helper remains in the same file.

## Running Experiments

Use the environment installed from the repository's requirements.txt and run scripts from the repository root, for example:

```bash
python experiments/gesture_test.py
```

Webcam tests use camera index 0. Photo and face-matching scripts expect the corresponding reference images in the working directory; supply them locally.

**Flight behavior:** `authorized_flight_test.py` and `pid_test_file.py` take off automatically, as does `../src/drone_control.py`. The file name "test" does not mean these scripts simulate hardware.

## Synchronization Notes

All ten uploaded Python scripts retain their original source contents. Three map to the existing src filenames; the others are retained here. The earlier assistant edit that reordered gesture checks and enabled classification labels has been replaced with the uploaded debug version.

`../src/finger_follow.py` remains a future-work placeholder. Application threading, PID finger-following, and integrated gesture-driven flight are not implemented in this snapshot.

# Gesture Recognition Drone

A Python computer-vision and drone-control project built around a DJI Tello. The goal is to combine owner face recognition, hand-gesture commands, and PID fingertip following.

**Current stage:** Debugging gesture classification in a standalone webcam prototype. Gesture recognition and drone flight control are **not integrated**. Threading and PID finger-following have not been started, and return-to-launch remains unfinished.

## Development Status

| Component | Status |
|---|---|
| Drone connection and basic flight commands | Implemented in a standalone flight test |
| Tello video stream and owner face recognition | Standalone face matching plus an authorized-flight experiment; takeoff occurs before the face check |
| Nine-gesture classifier | In development; classification accuracy is being debugged |
| Gesture-to-flight integration | Not integrated |
| Application threading | Not started |
| PID finger-following | Not started |
| Return-to-launch | Unfinished |
| Vision-based hover stabilization | Planned |
| Integrated state machine and demo video | Planned |

## Engineering Approach

The current gesture file is the uploaded PyCharm `normal_finger_detection.py`, preserved as `src/gesture_recognition.py`. It uses MediaPipe landmarks and OpenCV, and its active loop is intentionally configured to display finger-distance debugging values on a mirrored webcam feed. The file contains classification functions, but the current loop does not call them.

It explores:

- Landmark-distance comparisons using x, y, and z coordinates to estimate finger extension.
- A revised pointing-direction function using the vector from middle-finger base (landmark 9) to index-finger base (5), dot-product components in the y/z and x/y planes, and `atan2` angle sectors.
- An earlier wrist-based 2D projection helper retained for debugging.
- Rule-based classification for a vocabulary of nine gestures.

Reliable classification across hand poses and orientations is still being debugged. The classification functions return labels describing intended drone actions; they do not send flight commands.

See the [gesture-recognition development notes](docs/gesture-recognition-development.md) for the approaches explored and the coordinate-frame issues encountered.

## Planned Gesture Mapping

These are intended controls, not integrated flight capabilities.

| Gesture | Intended action |
|---|---|
| Open palm | Hover / stop |
| Closed fist | Approximate return-to-launch and land |
| Fingers crossed | Enter PID finger-follow mode |
| Point up | Ascend |
| Point down | Descend |
| Point left | Move left |
| Point right | Move right |
| Thumbs up | Move forward |
| Thumbs down | Move backward |

## Repository Guide

| File | Current role |
|---|---|
| [src/gesture_recognition.py](src/gesture_recognition.py) | Latest uploaded vector-projection prototype; active finger-distance debug display |
| [src/drone_control.py](src/drone_control.py) | Standalone automated takeoff, movement, rotation, and landing test |
| [src/face_auth.py](src/face_auth.py) | Face matching and labels over the Tello camera feed |
| [src/finger_follow.py](src/finger_follow.py) | Placeholder for future PID following |
| [experiments/](experiments/) | Supporting hand-tracking, crossed-finger, video, photo, authorized-flight, and velocity-reading scripts |
| [requirements.txt](requirements.txt) | Python dependencies |

See [experiments/README.md](experiments/README.md) for the original PyCharm filenames and the role of each overlapping script. Uploaded Python logic is preserved; these experiments capture development steps rather than one integrated application.

## Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/lo067291/Gesture-Recognition-Drone.git
cd Gesture-Recognition-Drone
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Dependencies include djitellopy, OpenCV, MediaPipe (pinned to 0.10.9), face-recognition, and NumPy. A tested Python/platform compatibility matrix has not yet been documented.

### Run the Webcam Gesture Prototype

A webcam is required; a drone is not required for this script.

```bash
python src/gesture_recognition.py
```

The script opens camera index `0`, draws hand landmarks, and displays `tip_dist`, `pip_dist`, and `index_extended` in the **Debug Values** window. This is the uploaded debug configuration; classification functions are present but are not called by the active loop. Press **q** to exit. Gesture classification remains an active development task.

### Run the Face-Recognition Prototype

Connect the computer to the Tello Wi-Fi network. Place a reference image named `owner_resized.jpg`, containing a detectable owner face, in the repository root; that image is not included in the repository.

```bash
python src/face_auth.py
```

This script streams the drone camera and labels recognized faces. It does not take off or enforce flight authorization. Press **q** in the OpenCV window to exit.

### Standalone Flight Test

`src/drone_control.py` automatically takes off, performs directional movements and rotations, then lands. Review the script before running it with a connected drone in a clear flight area with propeller guards. It is independent of both gesture classification and face recognition.

### Authorized-Flight Experiment

`experiments/authorized_flight_test.py` combines flight and face matching. It takes off first, scans for the owner for up to 10 seconds, then briefly hovers if a match is found or performs a 360-degree rejection rotation otherwise, before landing. Gesture control is still a placeholder. Run experiments from the repository root so relative image paths resolve correctly.

## Next Steps

1. Debug and validate gesture classification.
2. Implement application threading and integrate gesture output with flight control.
3. Implement PID finger-following.
4. Finish and validate approximate return-to-launch.
5. Integrate the state machine and record a demo.

## Limitations

- No end-to-end gesture-controlled flight workflow is available yet.
- Gesture accuracy and orientation robustness have not been established.
- The authorized-flight experiment checks identity after takeoff. Face recognition does not yet gate an integrated gesture-control system.
- The project uses a standard, non-EDU Tello. The intended return-to-launch behavior is approximate; a validated positioning approach is still needed.
- Vision-based hover stabilization and PID following are future work.

## Author

**Logan Stacy**  
Computer Engineering at UCF · Accelerated BS/MS  
CompTIA Security+ · CompTIA Network+

[LinkedIn](https://www.linkedin.com/in/logan-stacy) · [GitHub](https://github.com/lo067291) · [Student email](mailto:lo067291@ucf.edu)

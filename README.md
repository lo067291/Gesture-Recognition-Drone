# Gesture-Recognition-Drone

## Project Overview

A DJI Tello drone that only unlocks flight commands after 
recognizing its owner's face, then responds to hand gesture 
commands for navigation - including a "fingers crossed" gesture 
that activates fingertip-following mode.

## How It Works

1. Powers on and rises to a fixed hover height
2. Scans for owner's face within a timeout window
3. If authorized: unlocks gesture-based flight control
4. If not authorized: performs a rejection sequence (spin + land)
5. Gesture vocabulary maps hand signals to flight commands
6. "Fingers crossed" gesture activates fingertip-follow mode using 
   PID control
7. Closed fist gesture triggers approximate return-to-launch + land

## Gesture Vocabulary

| Gesture | Action |
|---|---|
| Open palm | Hover / Stop |
| Closed fist | Land (return home + land) |
| Fingers crossed | Enter finger-follow mode |
| Point up | Ascend |
| Point down | Descend |
| Point left | Move left |
| Point right | Move right |
| Thumbs up | Move forward |
| Thumbs down | Move backward |

## Development Status

- [x] Drone connection and basic flight control (djitellopy)
- [x] Live video stream via OpenCV
- [x] Face recognition owner authentication
- [x] Gesture classification (all 9 gestures, orientation-robust 
      using 3D landmark math)
- [ ] Gestures wired to live flight commands
- [ ] Finger-follow PID mode
- [ ] Vision-based hover stabilization
- [ ] Approximate return-to-launch
- [ ] Full state machine integration
- [ ] Demo video

## Technical Deep Dive

See [docs/gesture-recognition-development.md](docs/gesture-recognition-development.md) 
for a detailed writeup of the coordinate-frame problem encountered 
during gesture direction detection, and the vector math solution 
(hand-relative coordinate frames + dot product projection) used to 
solve it.

## Tech Stack

- **djitellopy** - drone flight control
- **OpenCV** - video stream processing
- **face_recognition** - owner authentication
- **MediaPipe** - hand landmark detection
- Python throughout

## Hardware

- DJI Tello (standard, non-EDU)
- Propeller guards (safety)

## Known Limitations

- Hover stabilization currently relies on Tello's onboard 
  stabilization; the standard (non-EDU) Tello's `get_speed_x/y` 
  telemetry does not return reliable real-time velocity data, so 
  active PID drift correction requires vision-based optical flow 
  from the camera feed instead (in progress)
- Return-to-launch is approximate, since standard Tello has no GPS 
  or absolute positioning - relies on accumulated displacement 
  tracking

## Author

**Logan Stacy**
- UCF Computer Engineering (BS/MS Accelerated - ISML Track)
- CompTIA Security+ & Network+ Certified
- [LinkedIn](https://linkedin.com/in/logan-stacy)
- [GitHub](https://github.com/lo067291)

# **Virtual Piano with Hand Tracking and MIDI Integration**

A Python-based virtual piano that uses computer vision to detect hand gestures and trigger MIDI notes. This project leverages OpenCV, MediaPipe, and the `rtmidi` library for real-time hand detection and MIDI output.

This project was developed as the final project for the Computer Vision course at Sapienza University.

---

## **Features**

- **Hand Detection**: Uses MediaPipe to detect and track hand landmarks.
- **MIDI Note Control**: Sends MIDI signals (Note ON/OFF) based on detected gestures.
- **Virtual Piano Visualization**: Displays a virtual piano on the screen with active keys highlighted.
- **Performance Monitoring**: Calculates and displays FPS and smoothed CPU usage during runtime.
- **Real-Time Skin Detection**: Enhances gesture recognition by detecting motion and skin regions.

---

## **How It Works**

1. **Hand Detection**:
   - Uses MediaPipe to detect hand landmarks and determine whether fingers are bent.
   - Finger gestures are mapped to corresponding piano keys.

2. **MIDI Signal Generation**:
   - Sends MIDI "Note ON" and "Note OFF" signals using the `rtmidi` library.
   - Allows interaction with any MIDI-supported software or hardware.

3. **Virtual Piano Display**:
   - Draws a virtual piano at the bottom of the screen using OpenCV.
   - Highlights active keys based on hand gestures.

4. **Performance Metrics**:
   - Tracks FPS and CPU usage to monitor real-time performance.
   - Smooths CPU usage using a moving average for better visualization.

---

## **Technologies Used**

- **Python**: Core programming language.
- **OpenCV**: For computer vision and visualization.
- **MediaPipe**: For real-time hand detection and tracking.
- **rtmidi**: For MIDI communication.
- **psutil**: To monitor CPU usage.
- **NumPy**: For efficient numerical operations.

---
## **Team Members**

- [Ehsan Mokhtari](https://github.com/sherlannn)
- [Hanieh Mahdavi](https://github.com/haniehm26)
- [Arash Bakhshaee Babaroud](https://github.com/ArashB1230)

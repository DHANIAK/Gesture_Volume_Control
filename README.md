# Gesture Volume Control

A real-time computer vision application that allows users to control their system volume using hand gestures.

## Overview

Gesture Volume Control uses a webcam to detect hand landmarks and recognize the distance between the thumb and index finger. This distance is mapped to the system volume, allowing touchless volume control without using a keyboard or mouse.

## Features

- Real-time hand detection using a webcam
- Tracks 21 hand landmarks using MediaPipe
- Controls system volume using thumb and index finger movement
- Uses OpenCV for real-time video processing
- Uses Pycaw to interact with the Windows system volume
- Touchless and intuitive user interaction

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Pycaw
- NumPy

## How It Works

1. The application accesses the webcam.
2. MediaPipe detects the user's hand.
3. The 21 hand landmarks are identified.
4. The distance between the thumb and index finger is calculated.
5. The distance is mapped to a volume percentage.
6. Pycaw changes the Windows system volume according to the detected gesture.

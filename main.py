import cv2
import time
import numpy as np
import pyautogui
import hand_tracking_module as htm

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Camera width and height
wCam, hCam = 1280, 720

print("Opening Camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Camera Opened")

cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

# Hand detector
print("Loading Hand Detector...")
detector = htm.HandDetector(detectionCon=0.5)
print("Hand Detector Ready")

# Volume setup
devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

volBar = 400
volPer = 0

# Cooldown for gestures
last_action_time = 0
cooldown = 2

while True:

    success, img = cap.read()

    if not success:
        continue

    # Detect hands
    img = detector.findHands(img)

    # Get landmark positions
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:

        # Thumb tip
        x1, y1 = lmList[4][1], lmList[4][2]

        # Index finger tip
        x2, y2 = lmList[8][1], lmList[8][2]

        # Center point
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw circles and line
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Distance calculation
        length = np.hypot(x2 - x1, y2 - y1)
        print("Distance =", length)

        # Volume control
        vol = np.interp(length, [30, 200], [minVol, maxVol])
        volBar = np.interp(length, [30, 200], [400, 150])
        volPer = np.interp(length, [30, 200], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)

        current_time = time.time()

        # ---------------- MUTE ----------------

        if length < 30:

            volume.SetMasterVolumeLevel(minVol, None)

            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

            cv2.putText(
                img,
                "MUTED",
                (200, 50),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (0, 0, 255),
                3
            )

        # ---------------- SCREENSHOT (THUMBS UP) ----------------

        thumb_tip_y = lmList[4][2]
        index_tip_y = lmList[8][2]
        middle_tip_y = lmList[12][2]
        ring_tip_y = lmList[16][2]
        pinky_tip_y = lmList[20][2]

        thumbs_up = (
            thumb_tip_y < index_tip_y and
            thumb_tip_y < middle_tip_y and
            thumb_tip_y < ring_tip_y and
            thumb_tip_y < pinky_tip_y
        )

        if thumbs_up and (current_time - last_action_time > cooldown):

            screenshot = pyautogui.screenshot()

            filename = f"screenshot_{int(time.time())}.png"

            screenshot.save(filename)

            cv2.putText(
                img,
                "SCREENSHOT SAVED",
                (180, 100),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (0, 255, 0),
                3
            )

            last_action_time = current_time

        # ---------------- PLAY / PAUSE (OPEN PALM) ----------------

        open_palm = (
            lmList[8][2] < lmList[6][2] and
            lmList[12][2] < lmList[10][2] and
            lmList[16][2] < lmList[14][2] and
            lmList[20][2] < lmList[18][2]
        )

        if open_palm and (current_time - last_action_time > cooldown):

            pyautogui.press("playpause")

            cv2.putText(
                img,
                "PLAY / PAUSE",
                (180, 150),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (255, 255, 0),
                3
            )

            last_action_time = current_time

    # Volume bar outline
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)

    # Filled volume bar
    cv2.rectangle(
        img,
        (50, int(volBar)),
        (85, 400),
        (255, 0, 0),
        cv2.FILLED
    )

    # Volume percentage
    cv2.putText(
        img,
        f'{int(volPer)} %',
        (35, 450),
        cv2.FONT_HERSHEY_COMPLEX,
        1,
        (255, 0, 0),
        3
    )

    # FPS calculation
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(
        img,
        f'FPS: {int(fps)}',
        (40, 50),
        cv2.FONT_HERSHEY_COMPLEX
        1,
        (255, 0, 0),
        3
    )

    cv2.imshow("Gesture Volume Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
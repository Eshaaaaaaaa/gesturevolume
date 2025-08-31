import cv2
import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ================= Volume Setup =================
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# Track mute status
isMuted = False

# ================= Mediapipe Setup =================
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# ================= Camera =================
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if lmList:
                # Thumb tip (id=4), Index tip (id=8)
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Draw landmarks
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

                # Distance between fingers
                length = np.hypot(x2 - x1, y2 - y1)

                # Map distance to volume range
                vol = np.interp(length, [30, 250], [minVol, maxVol])
                volume.SetMasterVolumeLevel(vol, None)

                # Volume Bar Display
                volBar = np.interp(length, [30, 250], [400, 150])
                cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
                cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

                # ===== Check for Fist (Mute/Unmute) =====
                fingerTips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
                fingerBases = [2, 6, 10, 14, 18]  # Joints below tips

                fingersClosed = True
                for tip, base in zip(fingerTips[1:], fingerBases[1:]):  # Ignore thumb
                    if lmList[tip][2] < lmList[base][2]:  # if fingertip higher than joint
                        fingersClosed = False
                        break

                if fingersClosed:
                    if not isMuted:
                        volume.SetMute(1, None)  # Mute
                        isMuted = True
                        cv2.putText(img, "MUTED", (200, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    if isMuted:
                        volume.SetMute(0, None)  # Unmute
                        isMuted = False
                        cv2.putText(img, "UNMUTED", (200, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Volume Control + Mute", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

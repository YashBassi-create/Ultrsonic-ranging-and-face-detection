import cv2
import os
import time
import sys
import numpy as np
from pathlib import Path

# --- CONFIGURATION ---
# Use OpenCV's bundled haarcascade path so users don't need to download manually.
FACE_CASCADE_PATH = os.path.join(
    cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
ALERT_COLOR = (0, 0, 255)  # BGR format: Bright Red for alert
NORMAL_COLOR = (0, 255, 0)  # BGR format: Bright Green for monitoring

# Load the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

# Check if the cascade file was loaded successfully
if face_cascade.empty():
    print(f"Error: Face cascade file not found at {FACE_CASCADE_PATH}")
    print("Please ensure OpenCV is installed correctly or place the 'haarcascade_frontalface_default.xml' file in OpenCV's data/haarcascades folder.")
    sys.exit(1)

# Initialize webcam (usually 0 is the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam. Make sure a camera is connected and not used by another application.")
    sys.exit(1)

print("Webcam started. Press 'q' to exit.")

# Variables for controlling the visual alert timer
face_detected_timer = 0
# Duration (in seconds) the red alert remains visible
VISUAL_ALERT_DURATION = 0.5

# Known face storage
BASE_DIR = Path(__file__).resolve().parent
KNOWN_DIR = BASE_DIR / 'known_faces'
KNOWN_DIR.mkdir(exist_ok=True)
KNOWN_FACE_PATH = KNOWN_DIR / 'known_face.jpg'

# Matching params
MATCH_SIZE = (100, 100)
MATCH_THRESHOLD = 0.6  # normalized matchTemplate threshold for recognition

try:
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces (returns a list of rectangles (x, y, w, h))
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        current_time = time.time()

        # --- ALERT/RECOGNITION LOGIC ---
        recognized_any = False
        detection_text = "Monitoring Active"
        detection_color = NORMAL_COLOR

        # Load known face if exists
        known_face = None
        if KNOWN_FACE_PATH.exists():
            known_face = cv2.imread(str(KNOWN_FACE_PATH), cv2.IMREAD_GRAYSCALE)
            if known_face is not None:
                known_face = cv2.resize(known_face, MATCH_SIZE)

        # For each detected face, try to match against known face
        for (x, y, w, h) in faces:
            # Extract face ROI and resize for matching
            face_roi_gray = gray[y:y+h, x:x+w]
            try:
                face_resized = cv2.resize(face_roi_gray, MATCH_SIZE)
            except Exception:
                # skip faces that are too small
                continue

            is_recognized = False
            if known_face is not None:
                # Use template matching on the resized face
                res = cv2.matchTemplate(
                    face_resized, known_face, cv2.TM_CCOEFF_NORMED)
                # res is single-channel; get max value
                if res.size == 1:
                    score = float(res)
                else:
                    _, score, _, _ = cv2.minMaxLoc(res)
                if score >= MATCH_THRESHOLD:
                    is_recognized = True

            if is_recognized:
                recognized_any = True
                color = NORMAL_COLOR
                text = "Welcome"
            else:
                color = ALERT_COLOR
                text = "INTRUDER ALERT! ACCESS DENIED"

            # Draw rectangle using the determined color
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            # Display text near the face
            cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # If no faces detected, show monitoring bar; if any recognized show welcome bar
        if len(faces) == 0:
            # Monitoring active bar
            cv2.putText(frame, "Monitoring Active", (5, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            if recognized_any:
                # green bar and welcome
                cv2.rectangle(
                    frame, (0, 0), (frame.shape[1], 30), NORMAL_COLOR, -1)
                cv2.putText(frame, "Welcome", (5, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                # red bar and intruder
                cv2.rectangle(
                    frame, (0, 0), (frame.shape[1], 30), ALERT_COLOR, -1)
                cv2.putText(frame, "INTRUDER ALERT! ACCESS DENIED", (5, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display the resulting frame
        cv2.imshow('Face Detection Security Scanner', frame)

        # Key controls:
        # 'q' - quit
        # 's' - save the largest detected face as known
        # 'r' - remove saved known face
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save largest face
            if len(faces) > 0:
                # pick largest by area
                largest = max(faces, key=lambda rect: rect[2]*rect[3])
                (x, y, w, h) = largest
                face_img = frame[y:y+h, x:x+w]
                face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                face_resized = cv2.resize(face_gray, MATCH_SIZE)
                cv2.imwrite(str(KNOWN_FACE_PATH), face_resized)
                print(f"Saved known face to {KNOWN_FACE_PATH}")
            else:
                print("No face to save. Position a face in view and press 's'.")
        elif key == ord('r'):
            if KNOWN_FACE_PATH.exists():
                KNOWN_FACE_PATH.unlink()
                print(f"Removed known face: {KNOWN_FACE_PATH}")
            else:
                print("No known face to remove.")

except KeyboardInterrupt:
    print("Exiting application.")
finally:
    # Cleanup webcam and window resources
    cap.release()
    cv2.destroyAllWindows()

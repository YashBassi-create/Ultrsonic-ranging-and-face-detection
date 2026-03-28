import cv2
import numpy as np
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@lru_cache(maxsize=128)
def load_face_cascade(cascade_path):
    """Loads and caches the haarcascade face detector.""" 
    return cv2.CascadeClassifier(cascade_path)

class FaceScanner:
    def __init__(self, cascade_path="haarcascade_frontalface_default.xml"):
        self.face_cascade = load_face_cascade(cascade_path)

    def scan(self):
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            logging.error("Could not open video device")
            return

        while True:
            ret, frame = video_capture.read()
            if not ret:
                logging.error("Failed to capture frame")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    scanner = FaceScanner()
    scanner.scan()

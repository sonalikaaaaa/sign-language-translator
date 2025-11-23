# import cv2
# import mediapipe as mp
# import numpy as np
# import torch
# import pyvirtualcam as pvc
# from ultralytics import YOLO

# # Mediapipe setup
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles
# mp_holistic = mp.solutions.holistic

# holistic = mp_holistic.Holistic(
#     min_detection_confidence=0.3,
#     min_tracking_confidence=0.3
# )

# # Webcam setup
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FPS, 30)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# if not cap.isOpened():
#     raise RuntimeError("Could not open webcam")

# # YOLO model
# model = YOLO('yolov5su.pt')

# # Draw landmarks
# def draw_landmarks(image, results):
#     if results.left_hand_landmarks:
#         mp_drawing.draw_landmarks(
#             image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
#             mp_drawing_styles.get_default_hand_landmarks_style()
#         )
#     if results.right_hand_landmarks:
#         mp_drawing.draw_landmarks(
#             image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
#             mp_drawing_styles.get_default_hand_landmarks_style()
#         )
#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(
#             image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
#             mp_drawing_styles.get_default_pose_landmarks_style()
#         )
#     return image

# # Main loop
# def collectData():
#     # Use OBS backend explicitly
#     with pvc.Camera(width=1280, height=720, fps=30, backend='obs') as cam:
#         print("Virtual camera started. Press Ctrl+C to exit.")
#         try:
#             while True:
#                 ret, frame = cap.read()
#                 if not ret:
#                     continue

#                 original = frame.copy()
#                 black = np.zeros_like(frame)

#                 image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 image_rgb.flags.writeable = False
#                 results = holistic.process(image_rgb)
#                 image_rgb.flags.writeable = True
#                 frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

#                 draw_landmarks(frame, results)
#                 draw_landmarks(black, results)

#                 # YOLO detection
#                 yolo_results = model(black)
#                 pred_img = np.squeeze(yolo_results.render())

#                 # Overlay detected class
#                 for r in yolo_results.pandas().xyxy[0].iterrows():
#                     if r[1]['confidence'] > 0.90:
#                         text = r[1]['name']
#                         print("Detected:", text)
#                         font = cv2.FONT_HERSHEY_DUPLEX
#                         cv2.putText(frame, text, (50, 100), font, 2, (255, 255, 255), 3, cv2.LINE_AA)

#                 # Send to virtual camera
#                 cam.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#                 cam.sleep_until_next_frame()

#         except KeyboardInterrupt:
#             print("Exiting...")

#     cap.release()
#     cv2.destroyAllWindows()

# collectData()
import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import pyvirtualcam as pvc
import pandas as pd

# Mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

holistic = mp_holistic.Holistic(
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)

# Webcam setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# YOLO model
model = YOLO('yolov5su.pt')  # use your local weights

# Draw landmarks on frame
def draw_landmarks(image, results):
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style()
        )
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style()
        )
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing_styles.get_default_pose_landmarks_style()
        )
    return image

# Main loop
def collectData():
    try:
        with pvc.Camera(width=1280, height=720, fps=30) as cam:
            print("Virtual camera started. Press Ctrl+C to exit.")

            while True:
                ret, frame = cap.read()
                if not ret:
                    continue

                original = frame.copy()
                black = np.zeros_like(frame)

                # Mediapipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = holistic.process(image_rgb)
                image_rgb.flags.writeable = True
                frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                draw_landmarks(frame, results)
                draw_landmarks(black, results)

                # YOLO detection
                yolo_results = model(black)
                for result in yolo_results:  
                    # df = result.pandas().xyxy[0]  # DataFrame of detections
                    boxes = result.boxes
                    df = pd.DataFrame(columns=["xmin","ymin","xmax","ymax","confidence","class","name"])
                  
                    if boxes is not None and len(boxes) > 0:
                        arr = boxes.data.cpu().numpy() 
                        df = pd.DataFrame(
                        arr,
                        columns=["xmin", "ymin", "xmax", "ymax", "confidence", "class"]
                        )  
                        df["name"] = [result.names[int(c)] for c in df["class"]]
                    for _, row in df.iterrows():
                        if row['confidence'] > 0.90:
                            text = row['name']
                            print("Detected:", text)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, text, (50, 100), font, 2, (255, 255, 255), 3, cv2.LINE_AA)

                # Send frame to virtual camera
                cam.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cam.sleep_until_next_frame()

    except KeyboardInterrupt:
        print("Exiting...")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    collectData()

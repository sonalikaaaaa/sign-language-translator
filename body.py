import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import torch
import yaml

with open("signLang/data.yaml", "r") as f:
    classes = yaml.safe_load(f)["names"]

classNames = classes

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

holistic = mp_holistic.Holistic(
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# model = torch.hub.load(
#     'ultralytics/yolov5',
#     'custom',
#     path='signLang/weights/best1.pt',
#     force_reload=False
# )

#model = YOLO("best1.pt")
model = YOLO("signLang/weights/best1.pt")


def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(
        image,
        results.left_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style()
    )
    mp_drawing.draw_landmarks(
        image,
        results.right_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style()
    )
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        mp_drawing_styles.get_default_pose_landmarks_style()
    )
    return image

letter = ""
offset = 1

# def collectData():
#     ret, frame = cap.read()
#     global letter

#     original = frame.copy()
#     crop_bg = np.zeros(frame.shape, dtype=np.uint8)
#     black = np.zeros(frame.shape, dtype=np.uint8)

#     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     image.flags.writeable = False
#     results_holistic = holistic.process(image)
#     image.flags.writeable = True
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     draw_landmarks(image, results_holistic)
#     draw_landmarks(black, results_holistic)

#     results = model(black)

#     pred_img = np.array(results.render()[0])

#     df = results.pandas().xyxy[0]
#     print("*******###length of df###****** " + str(len(df)))

#     for i, row in df.iterrows():
#         conf = float(row['confidence'])
#         print("####Conf is ####" + str(conf))
#         if conf < 0.8:
#             continue

#         name = row['name']
#         print(name + "****")

#         x1 = int(row['xmin']) - offset
#         y1 = int(row['ymin']) - offset
#         x2 = int(row['xmax']) + offset
#         y2 = int(row['ymax']) + offset

#         h, w = frame.shape[:2]
#         x1 = max(0, x1)
#         y1 = max(0, y1)
#         x2 = min(w - 1, x2)
#         y2 = min(h - 1, y2)

#         crop_img = pred_img[y1:y2, x1:x2]
#         crop_bg[y1:y2, x1:x2] = crop_img

#         return image, pred_img, original, crop_bg, name

#     return image, pred_img, original, crop_bg, letter


def collectData():
    ret, frame = cap.read()
    if not ret:
        return None, None, None, None, None

    original = frame.copy()

    # YOLO11 inference
    results = model(frame)

    # Annotated frame
    pred_img = results[0].plot()

    boxes = results[0].boxes

    name = ""
    crop_bg = None

    if len(boxes) > 0:
        box = boxes[0]
        cls = int(box.cls)
        name = classNames[cls]

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        crop_bg = frame[y1:y2, x1:x2]

    return frame, pred_img, original, crop_bg, name

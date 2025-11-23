# import pyvirtualcam
# import numpy as np

# frame = np.zeros((720, 1280, 3), dtype=np.uint8)

# with pyvirtualcam.Camera(width=1280, height=720, fps=30, backend='obs') as cam:
#     for i in range(100):
#         cam.send(frame)
#         cam.sleep_until_next_frame()
import cv2

cap = cv2.VideoCapture(0)

print("Camera opened:", cap.isOpened())

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Test Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

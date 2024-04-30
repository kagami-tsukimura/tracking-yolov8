import os

import cv2
from ultralytics import YOLO

output_dir = "./outputs"
output_file_path = f"{output_dir}/camera_tracking.mp4"

# 出力先なければ作成
os.makedirs("./outputs", exist_ok=True)

# カメラの読み込み
cap = cv2.VideoCapture(1)
# 1280*720 にリサイズ
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'));

CLIP_FPS = cap.get(cv2.CAP_PROP_FPS)
BG_COLOR = (79, 62, 70)
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

codec = cv2.VideoWriter_fourcc("m", "p", "4", "v")
video = cv2.VideoWriter(output_file_path, codec, CLIP_FPS, (W, H))
model = YOLO("./weights/yolov8s.pt")
fps = int(cap.get(cv2.CAP_PROP_FPS))

overlay_image = cv2.imread("./images/danger.png", cv2.COLOR_BGR2RGB)
overlay = cv2.resize(overlay_image, (W, H))

# 滞留カウンタ
counter = 0
is_person = False
# 閾値（人検知の連続フレーム数がこの値を超えたら警告）
person_thr = 100

# キーが押されるまで
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # YOLOv8でトラッキング
    results = model.track(frame, persist=True)
    result = results[0]

    boxes = result.boxes.xyxy.cpu().numpy().astype(int)
    try:
        ids = result.boxes.id.cpu().numpy().astype(int)
        cls_list = result.boxes.cls.cpu().numpy().astype(int)
        for box, id, cls in zip(boxes, ids, cls_list):
            cls_name = model.names[cls]
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    except Exception as e:
        print(e)
        print("There are no objects")
        continue
    finally:
        if is_person:
            counter += 1
            is_person = False
        else:
            counter = 0

        cv2.imshow("frame", frame)
        video.write(frame)


# videoの書き込み/読み込み終了
video.release()
cap.release()
cv2.destroyAllWindows()

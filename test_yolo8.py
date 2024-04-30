import os
import time

import cv2
from ultralytics import YOLO

output_dir = "./outputs"
file_path = "./videos/test.mp4"
output_file_path = f"{output_dir}/tracking.mp4"

# 出力先なければ作成
os.makedirs("./outputs", exist_ok=True)

# テスト動画の読み込み
cap = cv2.VideoCapture(file_path)

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

print("start detection")

# テスト動画に対してperson classのみで推論
results = model.track(
    source=file_path,
    tracker="bytetrack.yaml",
    # 人に限定して検知（すべて検知したい場合はclassesをコメントアウト）
    classes=[0],
    persist=True,
)

for result in results:
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
            if cls_name == "person":
                cv2.putText(
                    frame,
                    f"#{id} {cls_name} ({counter})",
                    (box[0], box[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    thickness=2,
                )
                is_person = True

                if counter >= person_thr:
                    frame = cv2.addWeighted(
                        src1=frame, alpha=0.99, src2=overlay, beta=0.3, gamma=0
                    )
            else:
                cv2.putText(
                    frame,
                    f"#{id} {cls_name}",
                    (box[0], box[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    1,
                )
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
        # 時間を元動画と合わせる
        time.sleep(1 / fps)
        cv2.imshow("frame", frame)
        video.write(frame)
        if cv2.waitKey(1) == 13:
            break
# videoの書き込み/読み込み終了
print("end detection")
video.release()
cap.release()
cv2.destroyAllWindows()

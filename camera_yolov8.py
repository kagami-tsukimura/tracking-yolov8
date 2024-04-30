import argparse
import os

import cv2
from ultralytics import YOLO


def parse_arguments():
    parser = argparse.ArgumentParser(description="Object detection with camera_yolov8")

    parser.add_argument(
        "-t", "--thr", default=100, type=int, help="Person continuous threshold"
    )
    parser.add_argument(
        "-cw", "--camera_width", default=1280, type=int, help="Sizes camera width"
    )
    parser.add_argument(
        "-ch", "--camera_height", default=720, type=int, help="Sizes camera height"
    )
    parser.add_argument(
        "-w",
        "--weights",
        default="./weights/yolov8s.pt",
        type=str,
        help="File path of object detection model",
    )

    args = parser.parse_args()

    print("arguments------")
    for key, value in vars(args).items():
        print(f"{key}: {value}")
    print("------arguments")

    return args


def release(video, cap):
    # videoの書き込み/読み込み終了
    print("end detection")
    video.release()
    cap.release()
    cv2.destroyAllWindows()


def main():
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
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    codec = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    video = cv2.VideoWriter(output_file_path, codec, CLIP_FPS, (W, H))
    model = YOLO("./weights/yolov8s.pt")

    overlay_image = cv2.imread("./images/danger.png", cv2.COLOR_BGR2RGB)
    overlay = cv2.resize(overlay_image, (W, H))

    # 滞留カウンタ
    counter = 0
    is_person = False
    # 閾値（人検知の連続フレーム数がこの値を超えたら警告）
    person_thr = 100

    print("start detection")

    # キーが押されるまで
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # YOLOv8でトラッキング
        results = model.track(frame, persist=True)
        result = results[0]

        # 推論結果からbboxの座標取得
        boxes = result.boxes.xyxy.cpu().numpy().astype(int)
        try:
            # 推論結果からbboxのクラスID取得
            ids = result.boxes.id.cpu().numpy().astype(int)
            # 推論結果からbboxのクラス名取得
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
                        2.0,
                        (0, 0, 255),
                        thickness=4,
                    )
                    is_person = True

                    if counter >= person_thr:
                        # Alert!
                        frame = cv2.addWeighted(
                            src1=frame, alpha=0.8, src2=overlay, beta=0.3, gamma=0
                        )
                else:
                    cv2.putText(
                        frame,
                        f"#{id} {cls_name}",
                        (box[0], box[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        thickness=1,
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

            cv2.imshow("frame", frame)
            video.write(frame)
            key = cv2.waitKey(1)
            if key != -1:
                print("STOP PLAY!!!")
                break

    release(video, cap)


if __name__ == "__main__":

    args = parse_arguments()
    main()

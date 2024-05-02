import argparse
import asyncio
import json
import os
from datetime import datetime
from enum import Enum

import cv2
import requests
from ultralytics import YOLO


class AlertStatus(Enum):
    CAMERA = "CAMERA"
    MP4 = "MP4"


def print_arguments(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print("arguments------")
        for key, value in vars(result).items():
            print(f"{key}: {value}")
        print("------arguments")
        return result

    return wrapper


@print_arguments
def parse_arguments():
    now = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")

    parser = argparse.ArgumentParser(description="Object detection with camera_yolov8")

    parser.add_argument(
        "-v",
        "--video",
        default="",
        type=str,
        help="Input file path",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=f"{now}_tracking.mp4",
        type=str,
        help="Output file path",
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
    parser.add_argument(
        "-t", "--thr", default=100, type=int, help="Person continuous threshold"
    )
    parser.add_argument(
        "-u", "--url", default="http://localhost:8000", type=str, help="POST URL"
    )
    parser.add_argument(
        "-n", "--nginx", default="http://localhost:8001", type=str, help="Nginx URL"
    )

    return parser.parse_args()


def post_picture(url, alert_image_path):
    try:
        res = requests.post(
            f"{url}/picture",
            json={"picture": alert_image_path},
            timeout=10,
        )
        print("POST request sent successfully.")

        res_picture_id = json.loads(res.text)["picture_id"]

        return res_picture_id
    except Exception as e:
        print(f"Failed to send POST picture request: {e}")


async def post_alert(url, picture_id, status, alert_file):
    try:
        res = await asyncio.to_thread(
            requests.post,
            f"{url}/alert",
            json={"picture_id": picture_id, "status": status},
            timeout=10,
        )
        print("POST request sent successfully.")

        res_picture = json.loads(res.text)["picture"]

        with open(alert_file, "a") as f:
            f.write(f"{res_picture}\n")
    except Exception as e:
        print(f"Failed to send POST alert request: {e}")


def release(video, cap):
    # videoの書き込み/読み込み終了
    print("end detection")
    video.release()
    cap.release()
    cv2.destroyAllWindows()


def main(args):
    # 定数
    PERSON = "person"
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    SMALL = 1
    MEDIUM = 2
    LARGE = 4

    alert_dir = "./alerts"
    output_dir = "./outputs"
    output_file_path = f"{output_dir}/{args.output}"

    # 出力先がなければ作成
    os.makedirs(alert_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    if args.video:
        cap = cv2.VideoCapture(args.video)
        alpha = 0.99
        alert_status = AlertStatus.MP4.value
    else:
        # カメラの読み込み
        cap = cv2.VideoCapture(0)
        alpha = 0.8
        alert_status = AlertStatus.CAMERA.value
    # camera_width*camera_height にリサイズ
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.camera_height)

    # FPS確保のため圧縮
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'));

    CLIP_FPS = cap.get(cv2.CAP_PROP_FPS)
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    codec = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    video = cv2.VideoWriter(output_file_path, codec, CLIP_FPS, (W, H))
    model = YOLO(args.weights)

    danger_file_path = "./images/danger.png"
    overlay_image = cv2.imread(danger_file_path, cv2.COLOR_BGR2RGB)
    overlay = cv2.resize(overlay_image, (W, H))

    # 滞留カウンタ
    counter = 0
    is_person = False
    # 閾値（人検知の連続フレーム数がこの値を超えたら警告）
    person_thr = args.thr

    # アラート（一度きり）
    is_before_alert = True

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
                cv2.rectangle(
                    frame,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    color=GREEN,
                    thickness=MEDIUM,
                )
                if cls_name == PERSON:
                    cv2.putText(
                        frame,
                        f"#{id} {cls_name} ({counter})",
                        (box[0], box[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=MEDIUM,
                        color=RED,
                        thickness=LARGE,
                    )
                    is_person = True

                    if counter >= person_thr:
                        # Alert!
                        frame = cv2.addWeighted(
                            src1=frame, alpha=alpha, src2=overlay, beta=0.3, gamma=0
                        )
                        # 並列処理でpost送信
                        if is_before_alert:
                            is_before_alert = False
                            now = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
                            alert_file = f"{now}_person_keikoku.png"
                            alert_image_path_nginx = f"{args.nginx}/images/{alert_file}"
                            alert_image_path_local = (
                                f"server/docker/nginx/images/{alert_file}"
                            )
                            print("ALERT!!")

                            # picture post
                            picture_id = post_picture(args.url, alert_image_path_nginx)
                            loop = asyncio.get_event_loop()
                            # alert post
                            loop.run_until_complete(
                                post_alert(
                                    args.url,
                                    picture_id,
                                    alert_status,
                                    f"{alert_dir}/alert.txt",
                                )
                            )
                            # nginxに画像保存
                            cv2.imwrite(
                                alert_image_path_local,
                                frame,
                            )

                else:
                    cv2.putText(
                        frame,
                        f"#{id} {cls_name}",
                        (box[0], box[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=SMALL,
                        color=BLUE,
                        thickness=SMALL,
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
    main(args)

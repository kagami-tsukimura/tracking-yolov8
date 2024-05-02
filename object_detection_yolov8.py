import argparse
import asyncio
import json
import logging
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
    """
    A decorator function that wraps another function and prints the arguments and their values before calling the original function.

    Parameters:
        func (callable): The original function to be wrapped.

    Returns:
        callable: The wrapper function that prints the arguments and their values before calling the original function.
    """

    def wrapper(*args, **kwargs):
        """
        A wrapper function that prints the arguments and their values before calling the original function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the original function.
        """

        setting_logger()
        result = func(*args, **kwargs)
        print("arguments------")
        for key, value in vars(result).items():
            print(f"{key}: {value}")
        print("------arguments")
        return result

    def setting_logger():
        """
        Sets up the logger for the application.

        This function creates a directory named "logs" if it doesn't already exist and configures.
        Logging module to write logs to a file named "logger.log" inside the "logs" directory.
        Log level is set to INFO, and the log message format includes the timestamp, log level, and the log message itself.

        Parameters:
            None

        Returns:
            None
        """
        LOG_DIR = "./logs"
        os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(
            filename=f"{LOG_DIR}/logger.log",
            level=logging.INFO,
            format="{asctime} [{levelname:.4}] {message}",
            style="{",
        )
        logging.info("start detection")

    return wrapper


@print_arguments
def parse_arguments():
    """
    Parse the command line arguments for object detection with camera_yolov8.

    Returns:
        argparse.Namespace: The parsed command line arguments.

    Raises:
        SystemExit: If an error occurs while parsing the command line arguments.
    """

    try:
        now = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
        parser = argparse.ArgumentParser(
            description="Object detection with camera_yolov8"
        )

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
    except Exception as e:
        logging.error(f"Failed to parse arguments: {e}")
        raise SystemExit

    return parser.parse_args()


def post_picture(url, alert_image_path):
    """
    Sends a POST request to the specified URL with the provided alert image path.

    Args:
        url (str): The URL to send the POST request to.
        alert_image_path (str): The path to the alert image.

    Returns:
        The ID of the picture received from the POST request.

    Raises:
        Exception: If the POST request fails.
    """

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
        logging.error(f"Failed to send POST picture request: {e}")


async def post_alert(url, picture_id, status, alert_file):
    """
    Async sends a POST request to the specified URL with the given picture ID, status, and alert file.

    Args:
        url (str): The URL to send the POST request to.
        picture_id (int): The ID of the picture.
        status (str): The status of the alert.
        alert_file (str): The path to the alert file.

    Returns:
        None

    Raises:
        Exception: If the POST request fails to send.
    """

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
        logging.error(f"Failed to send POST alert request: {e}")


def release(video, cap):
    """
    Release the video and camera resources.

    Args:
        video (cv2.VideoWriter): The video writer object.
        cap (cv2.VideoCapture): The video capture object.

    Returns:
        None
    """
    # videoの書き込み/読み込み終了
    print("end detection")
    video.release()
    cap.release()
    cv2.destroyAllWindows()


def main(args):
    """
    The main function that performs object detection using YOLOv8 and displays the results in a video stream.

    Parameters:
    - args: A dictionary containing the command line arguments passed to the function.
        - video: The path to the video file to be processed.
        - weights: The path to the YOLOv8 weights file.
        - output: The name of the output video file.
        - camera_width: The width of the camera frame.
        - camera_height: The height of the camera frame.
        - thr: The threshold for detecting people.

    Returns:
    - None

    This function performs the following steps:
    1. Sets up the necessary directories and files.
    2. Reads the video file or initializes the camera stream.
    3. Sets the frame size and FPS of the video.
    4. Initializes the YOLOv8 model.
    5. Loads the overlay image for the alert.
    6. Enters the detection loop, which continues until the video is finished or the user presses a key.
    7. Reads a frame from the video.
    """

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

    try:
        if args.video:
            cap = cv2.VideoCapture(args.video)
            alpha = 0.99
            alert_status = AlertStatus.MP4.value
        else:
            # カメラの読み込み
            cap = cv2.VideoCapture(0)
            alpha = 0.8
            alert_status = AlertStatus.CAMERA.value
    except Exception as e:
        logging.error(f"Failed to video capture: {e}")

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
    logging.info("start detection")

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
                            alert_image_path_nginx = f"{args.nginx}/{alert_file}"
                            alert_image_path_local = (
                                f"server/docker/nginx/images/{alert_file}"
                            )
                            print("ALERT!!")
                            logging.info("ALERT!!")

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
                logging.warning("STOP PLAY!!!")
                break

    release(video, cap)


if __name__ == "__main__":

    args = parse_arguments()
    main(args)

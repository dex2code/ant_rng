from config import *
from loguru import logger

logger.info("*** Ant True RNG ***")
logger.info("Loading libraries...")
import sys, cv2, time, json
from datetime import datetime
from uuid import uuid4
from ultralytics import YOLO


@logger.catch
def post_process_image(input_image, ant_detections):
    output_image = input_image

    output_dict = {}

    image_uuid = str(uuid4())
    output_dict['uuid'] = image_uuid

    image_dt = datetime.now()
    image_ts_str = str(int(datetime.timestamp(image_dt)))
    image_dt_str = image_dt.strftime("%d.%m.%Y %H:%M:%S")
    output_dict['timestamp'] = image_ts_str
    output_dict['datetime'] = image_dt_str

    if SAVE_RAW_CAPTURES:
        try:
            cv2.imwrite(f"{RAW_CAPTURES_DIR}/{image_ts_str}.png", input_image)
        except Exception as E:
            logger.warning(f"Cannot save raw image to {RAW_CAPTURES_DIR}/{image_ts_str}.png (str(E))")

    output_dict['coordinates'] = []

    for ant_detection in ant_detections:
        for ant_box in ant_detection.boxes.xyxy:
            x1 = int(ant_box[0])
            y1 = int(ant_box[1])
            x2 = int(ant_box[2])
            y2 = int(ant_box[3])

            output_dict['coordinates'].append(x1)
            output_dict['coordinates'].append(y1)
            output_dict['coordinates'].append(x2)
            output_dict['coordinates'].append(y2)

            output_image = cv2.rectangle(output_image, (x1, y1), (x2, y2), (255, 255, 255), 1)
            output_image = cv2.putText(output_image, f"({x1}, {y1})", (x1, y1-10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)

    image_height, image_width, image_channels = output_image.shape

    output_image = cv2.putText(output_image, "ANT true RNG", (22, 42), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    output_image = cv2.putText(output_image, "ANT true RNG", (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (240, 240, 240), 2, cv2.LINE_AA)

    output_image = cv2.line(output_image, (0, 62), (300, 62), (0, 0, 0), 2)
    output_image = cv2.line(output_image, (0, 60), (300, 60), (255, 255, 255), 2)

    output_image = cv2.putText(output_image, f"UUID: {image_uuid}", (10, image_height-30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
    output_image = cv2.putText(output_image, f"UUID: {image_uuid}", (12, image_height-32), cv2.FONT_HERSHEY_PLAIN, 1, (240, 240, 240), 1, cv2.LINE_AA)

    output_image = cv2.putText(output_image, f"Timestamp: {image_ts_str} ({image_dt_str})", (10, image_height-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
    output_image = cv2.putText(output_image, f"Timestamp: {image_ts_str} ({image_dt_str})", (12, image_height-12), cv2.FONT_HERSHEY_PLAIN, 1, (240, 240, 240), 1, cv2.LINE_AA)

    return output_image, output_dict


@logger.catch
def main():
    logger.info("Running main()")

    ant_model = YOLO(YOLO_MODEL_FILE)
    logger.info(f"Loaded model {YOLO_MODEL_FILE=}")

    while True:
        try:
            camera = cv2.VideoCapture(CAMERA_DEVICE_NUM, cv2.CAP_V4L)
            time.sleep(CAMERA_COOLDOWN_TIMEOUT_SEC)

            camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION_HEIGHT)
            time.sleep(CAMERA_COOLDOWN_TIMEOUT_SEC)

            camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            camera.set(cv2.CAP_PROP_FOCUS, CAMERA_FOCUS_VALUE)
            time.sleep(CAMERA_COOLDOWN_TIMEOUT_SEC)

            camera.set(cv2.CAP_PROP_CONTRAST, CAMERA_CONTRAST_VALUE)
            camera.set(cv2.CAP_PROP_BRIGHTNESS, CAMERA_BRIGHTNESS_VALUE)
            camera.set(cv2.CAP_PROP_SHARPNESS, CAMERA_SHARPNESS_VALUE)
            camera.set(cv2.CAP_PROP_ZOOM, CAMERA_ZOOM_VALUE)
            time.sleep(CAMERA_COOLDOWN_TIMEOUT_SEC)

        except Exception as E:
            logger.error(f"Cannot open {CAMERA_DEVICE_NUM=} ({str(E)})")
        else:
            logger.info(f"{CAMERA_DEVICE_NUM=} opened")

        capture_result = 0
        if camera.isOpened():
            try:
                camera.grab()
                time.sleep(CAMERA_COOLDOWN_TIMEOUT_SEC)
                capture_result, captured_image = camera.read()
                camera.release()
                logger.info(f"Captured image successfully")
            except Exception as E:
                logger.error(f"Error capture the image with {CAMERA_DEVICE_NUM=} ({str(E)})")
        else:
            logger.warning(f"{CAMERA_DEVICE_NUM=} is not opened")

        if capture_result:
            try:
                ant_detections = ant_model.predict(source=captured_image, show=False, save=YOLO_SAVE_IMG, conf=YOLO_CONFIDENCE_VALUE, iou=YOLO_IOU_VALUE)

                post_processed_image, result_dict = post_process_image(captured_image, ant_detections)

                json_object = json.dumps(result_dict, indent=4)
                with open(f"{RESULT_DIR}/{RESULT_JSON_NAME}", "w") as outfile:
                    outfile.write(json_object)

                cv2.imwrite(f"{RESULT_DIR}/{RESULT_IMG_NAME}", post_processed_image)
            except Exception as E:
                logger.error(f"Cannot operate the image ({str(E)})")
            else:
                logger.info(f"Successfully saved result")
        else:
            logger.warning(f"No image captured {capture_result=}")

        logger.info(f"Pause for {CAPTURE_PAUSE_SEC=}")
        time.sleep(CAPTURE_PAUSE_SEC)


if __name__ == "__main__":
    logger.info("Entering main()")
    sys.exit(main())

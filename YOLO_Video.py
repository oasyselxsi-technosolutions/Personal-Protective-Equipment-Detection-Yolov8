from datetime import datetime
from ultralytics import YOLO
import cv2

import math
import os
import config
from dotenv import load_dotenv
load_dotenv()
DETECTION_RESULTS_FILE = os.getenv("DETECTION_RESULTS_FILE", "detection_results.txt")
start_time = datetime.now()
detection_results = []

# --- Violation Alert Integration ---
import requests
def send_violation_alert(violation):
    try:
        requests.post('http://localhost:5000/api/violation_alert', json=violation, timeout=1)
    except Exception as e:
        print(f"[YOLO] Alert API call failed: {e}")


def video_detection(path_x):
    global start_time, detection_results
    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO("YOLO-Weights/bestest.pt")
    classNames = ['Excavator', 'Gloves', 'Hardhat', 'Ladder', 'Mask', 'NO-hardhat',
                  'NO-Mask', 'NO-Safety Vest', 'Person', 'SUV', 'Safety Cone', 'Safety Vest',
                  'bus', 'dump truck', 'fire hydrant', 'machinery', 'mini-van', 'sedan', 'semi',
                  'trailer', 'truck and trailer', 'truck', 'van', 'vehicle', 'wheel loader']

    # Initialize variables
    # start_time = datetime.now()
    # detection_results = []

    while True:
        success, img = cap.read()
        if not success:
            break  # Exit the loop if the video ends or cannot be read

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f'{class_name}{conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                c2 = x1 + t_size[0], y1 - t_size[1] - 3

                if class_name == 'Hardhat':
                    color = (0, 204, 255)
                elif class_name == "Gloves":
                    color = (222, 82, 175)
                elif class_name == "NO-hardhat":
                    color = (0, 100, 150)
                elif class_name == "Mask":
                    color = (0, 180, 255)
                elif class_name == "NO-Safety Vest":
                    color = (0, 230, 200)
                elif class_name == "Safety Vest":
                    color = (0, 266, 280)
                else:
                    color = (85, 45, 255)

                if conf > 0.6:
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)
                    cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

                    # Check if the class is NO-Mask, NO-Safety Vest, or NO-hardhat and confidence is above threshold

                    if class_name in ['NO-Mask', 'NO-Safety Vest', 'NO-hardhat']:
                        detection = {
                            'type': class_name,
                            'confidence': conf,
                            'bbox': (x1, y1, x2, y2),
                            'location': 'Unknown',  # You can set this based on camera/domain
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        detection_results.append(detection)
                        # Send deduplicated alert to backend
                        send_violation_alert(detection)

        # Display the video frame with detections
        cv2.imshow("YOLO Detection", img)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Save detection results every 30 seconds
        if (datetime.now() - start_time).seconds >= 30:
            with open('detection_results.txt', 'a') as file:
                for detection in detection_results:
                    file.write(f"[ {detection['time']} ] {detection['class']} {detection['confidence']} {detection['bounding_box']} \n")
                file.write('\n')  # Add a newline to separate each 30-second interval
            
            start_time = datetime.now()
            detection_results = []

    cap.release()
    cv2.destroyAllWindows()

def manufacturing_video_detection(video_path):
    import cv2
    from ultralytics import YOLO

    cap = cv2.VideoCapture(video_path)
    model = YOLO("YOLO-Weights/bestest.pt")
    print(" Inside manufacturing_video_detection")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Call your manufacturing PPE detection method
        frame = detect_manufacturing_ppe(frame, model)

        cv2.imshow("Manufacturing PPE Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def video_detection_single_frame(frame):
    """Process a single frame with YOLO detection."""
    model = YOLO("YOLO-Weights/bestest.pt")
    classNames = ['Excavator', 'Gloves', 'Hardhat', 'Ladder', 'Mask', 'NO-hardhat',
                  'NO-Mask', 'NO-Safety Vest', 'Person', 'SUV', 'Safety Cone', 'Safety Vest',
                  'bus', 'dump truck', 'fire hydrant', 'machinery', 'mini-van', 'sedan', 'semi',
                  'trailer', 'truck and trailer', 'truck', 'van', 'vehicle', 'wheel loader']

    results = model(frame, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            class_name = classNames[cls]
            label = f'{class_name}{conf}'
            t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] - 3

            if class_name == 'Hardhat':
                color = (0, 204, 255)
            elif class_name == "Gloves":
                color = (222, 82, 175)
            elif class_name == "NO-hardhat":
                color = (0, 100, 150)
            elif class_name == "Mask":
                color = (0, 180, 255)
            elif class_name == "NO-Safety Vest":
                color = (0, 230, 200)
            elif class_name == "Safety Vest":
                color = (0, 266, 280)
            else:
                color = (85, 45, 255)

            if conf > 0.6:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.rectangle(frame, (x1, y1), c2, color, -1, cv2.LINE_AA)
                cv2.putText(frame, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

    return frame

def detect_manufacturing_ppe(frame, model):
    positive_classes = ['Person','Mask','Hardhat', 'Gloves', 'Safety goggles', 'Ear protection', 'Face shield', 'Steel-toe boots', 'Apron', 'Protective suit', 'Respirator','Safety Vest']
    negative_classes = ['NO-hardhat', 'NO-Mask', 'NO-Safety Vest']
    return detect_ppe_by_domain(frame, model, positive_classes, negative_classes,domain_name="Manufacturing")

def detect_construction_ppe(frame, model):
    positive_classes = ['Person','Hardhat', 'Safety Vest', 'Safety boots']
    negative_classes = ['NO-hardhat', 'NO-Mask', 'NO-Safety Vest']
    return detect_ppe_by_domain(frame, model, positive_classes, negative_classes,domain_name="Construction")

def detect_healthcare_ppe(frame, model):
    positive_classes = ['Person','Mask', 'Gloves', 'Face shield', 'Gown', 'N95 mask', 'Safety goggles', 'Shoe cover', 'Hair net', 'Hazmat suit']
    negative_classes = ['NO-Mask', 'NO-Gown', 'NO-Gloves']
    return detect_ppe_by_domain(frame, model, positive_classes, negative_classes,domain_name="Healthcare")

def detect_oilgas_ppe(frame, model):
    positive_classes = ['Person','Hardhat', 'Flame-resistant clothing', 'Safety goggles', 'Ear protection', 'Safety boots', 'Gloves', 'Respirator', 'Full-body suit', 'Face shield']
    negative_classes = ['NO-hardhat', 'NO-Mask', 'NO-Safety Vest']
    return detect_ppe_by_domain(frame, model, positive_classes, negative_classes, domain_name="Oil & Gas")

def detect_ppe_by_domain(frame, model, positive_classes, negative_classes, domain_name="PPE Detection"):
    global start_time, detection_results
    classNames = [
        'Excavator', 'Gloves', 'Hardhat', 'Ladder', 'Mask', 'NO-hardhat',
        'NO-Mask', 'NO-Safety Vest', 'Person', 'SUV', 'Safety Cone', 'Safety Vest',
        'bus', 'dump truck', 'fire hydrant', 'machinery', 'mini-van', 'sedan', 'semi',
        'trailer', 'truck and trailer', 'truck', 'van', 'vehicle', 'wheel loader'
    ]
    # Draw the domain name at the top-left
    cv2.putText(frame, domain_name, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, domain_name, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 2, cv2.LINE_AA)

    # Display recording status below the domain name
    recording_status = f"Recording: {'ON' if config.violation_recording_enabled else 'OFF'}"
    cv2.putText(frame, recording_status, (10, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, recording_status, (10, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.45, (0, 255, 0) if config.violation_recording_enabled else (0, 0, 255), 1, cv2.LINE_AA)

    violation_detected = False  # <-- Initialize here


    results = model(frame, stream=True)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            if 0 <= cls < len(classNames):
                class_name = classNames[cls]
            else:
                class_name = f"Unknown({cls})"
            label = f'{class_name} {conf:.2f}'
            if class_name == "Person":
                color = (255, 255, 255)  # WHITE
            elif class_name in negative_classes:
                color = (0, 0, 255)  # RED
                if conf > 0.6:
                    violation_detected = True  # <-- Set to True if violation found
                      # Add detection result with domain_name
                   # Generate timestamp ONCE for this violation
                    violation_time = datetime.now()
                    violation_time_str = violation_time.strftime('%Y-%m-%d %H:%M:%S')
                    violation_time_file = violation_time.strftime('%Y%m%d_%H%M%S_%f')
                    detection_results.append({
                        'domain': domain_name,
                        'class': class_name,
                        'confidence': conf,
                        'bounding_box': (x1, y1, x2, y2),
                        'time': violation_time_str,
                        'file_time': violation_time_file  # Add this for filename use
                    })
            elif class_name in positive_classes:
                color = (0, 255, 0)  # GREEN
            else:
                color = (85, 45, 255)  # default
            if conf > 0.6:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                # Set label color: red for violations, white otherwise
                label_color = (0, 0, 255) if class_name in negative_classes else (255, 255, 255)
                cv2.putText(frame, label, (x1, y1 - 2), 0, 1, label_color, 1, cv2.LINE_AA)

    
    if (datetime.now() - start_time).seconds >= 30:
        with open(DETECTION_RESULTS_FILE, 'a') as file:
            for detection in detection_results:
                file.write(
                    f"[{detection['time']}] [{detection['domain']}] {detection['class']} {detection['confidence']} {detection['bounding_box']}\n"
                )
            file.write('\n')  # Add a newline to separate each 30-second interval
            print(f"[DEBUG] Finished writing to {DETECTION_RESULTS_FILE}")
            start_time = datetime.now()
            detection_results = []
    # Save frame if violation detected and recording is enabled
    print(f"[DEBUG] violation_detected={violation_detected}, violation_recording_enabled={config.violation_recording_enabled}")
    if violation_detected and config.violation_recording_enabled:
        # Use the last violation's timestamp for the filename
        last_violation = detection_results[-1] if detection_results else None
        if last_violation:
            domain_short = ''.join([c for c in domain_name if c.isalnum()])[:4]
            save_dir = f"static/violations/{domain_short}"
            os.makedirs(save_dir, exist_ok=True)
            filename = f"{save_dir}/violation_{domain_name}_{last_violation['file_time']}.jpg"
            print(f"Violation detected! Saving frame to {filename}")

            # Draw the violation timestamp at the bottom right of the frame
            violation_time_str = last_violation['time']
            h, w = frame.shape[:2]
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            (text_width, text_height), _ = cv2.getTextSize(violation_time_str, font, font_scale, thickness)
            x = w - text_width - 10
            y = h - 10
            cv2.putText(frame, violation_time_str, (x, y), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
            cv2.putText(frame, violation_time_str, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            cv2.imwrite(filename, frame)

    # === Add this block here ===
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    (text_width, text_height), _ = cv2.getTextSize(now_str, font, font_scale, thickness)
    x = w - text_width - 10
    y = h - 10
    cv2.putText(frame, now_str, (x, y), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, now_str, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    # ===========================
    return frame


if __name__ == "__main__":
    # Replace 'path_to_video.mp4' with the actual path to your video file
    video_path = "/home/yunusparvej/workpackages/consultancy_ws/Personal_Protective_Equipment_Detection/Personal-Protective-Equipment-Detection-Yolov8/static/files/8bb9137c12_Test1.mp4"
    # video_detection(video_path)
    manufacturing_video_detection(video_path)

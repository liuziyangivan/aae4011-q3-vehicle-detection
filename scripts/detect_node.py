#!/usr/bin/env python3
"""
ROS Noetic UAS Vehicle Detection Node (Ubuntu 20.04)
AAE4011 Q3 - Core Detection Pipeline
Dependencies: YOLOv8n, OpenCV4, numpy (for CompressedImage decoding)
Core Functions:
1. Real-time rosbag playback and CompressedImage reading
2. YOLOv8n vehicle detection (Car/Bus/Truck only)
3. Draw bounding boxes, labels and confidence scores
4. Publish detection results to ROS topic (/detect/result_image)
5. Visualization with OpenCV window and RQT (ROS official)
"""
import rospy
import rosbag
import cv2
import os
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image, CompressedImage
from ultralytics import YOLO

# Global Initialization (Noetic Python3 compatible)
bridge = CvBridge()
# Load YOLOv8 nano (lightweight, fast for UAS - 6MB model)
model = YOLO("yolov8n.pt")
# ROS Publisher for detection results (for RQT visualization)
detect_pub = None

# COCO Dataset Vehicle Classes (fixed for assignment)
# 2 = Car, 5 = Bus, 7 = Truck (filter other classes for speed)
VEHICLE_CLASSES = [2, 5, 7]
CLASS_MAP = {2: "Car", 5: "Bus", 7: "Truck"}
# Get script path (Noetic relative path fix)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(SCRIPT_DIR, "..")

def draw_detections(img, results, frame_num):
    """
    Draw detection results on image (MANDATORY for assignment criterion)
    Input: OpenCV image, YOLO results, current frame number
    Output: Annotated image, total detected vehicles
    Annotations: Red bounding box, white label (class+conf), green statistics
    """
    vehicle_count = 0
    for res in results:
        boxes = res.boxes
        for box in boxes:
            # Filter only vehicle classes
            cls_id = int(box.cls)
            if cls_id not in VEHICLE_CLASSES:
                continue
            vehicle_count += 1

            # Get bounding box coordinates (x1,y1=top-left; x2,y2=bottom-right)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Get confidence score (0-1)
            conf = round(float(box.conf), 2)
            # Class name
            cls_name = CLASS_MAP[cls_id]

            # Draw red bounding box (thickness=2, Noetic visual standard)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # Create label text (Class: Confidence)
            label = f"{cls_name}: {conf}"
            # Calculate text size for background box (avoid overlap)
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            # Draw red background for label (improve readability)
            cv2.rectangle(img, (x1, y1-text_h-5), (x1+text_w, y1), (0, 0, 255), -1)
            # Draw white label text
            cv2.putText(img, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Draw statistics (frame number + vehicle count) - bottom-left corner
    stats = f"Frame: {frame_num} | Detected Vehicles: {vehicle_count}"
    cv2.putText(img, stats, (10, img.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img, vehicle_count

def process_image(cv_img, frame_num):
    """
    Process single image frame: YOLO detection + annotation + ROS publish
    Input: OpenCV image, frame number
    Output: Annotated OpenCV image
    """
    # Get ROS parameters (confidence + IOU threshold)
    conf_thres = rospy.get_param("/conf_thres", 0.25)
    iou_thres = rospy.get_param("/iou_thres", 0.45)

    # YOLOv8 inference (filter vehicle classes for speed, Noetic real-time)
    results = model(
        cv_img,
        conf=conf_thres,
        iou=iou_thres,
        classes=VEHICLE_CLASSES,
        verbose=False  # Disable YOLO log to avoid terminal spam
    )

    # Draw detection results
    annotated_img, _ = draw_detections(cv_img, results, frame_num)

    # Publish annotated image to ROS topic (for RQT image view)
    try:
        ros_img = bridge.cv2_to_imgmsg(annotated_img, encoding="bgr8")
        detect_pub.publish(ros_img)
    except CvBridgeError as e:
        rospy.logerr(f"[Detection] CVBridge error: {str(e)}")

    return annotated_img

def real_time_detection():
    """Main real-time detection function (rosbag playback for CompressedImage)"""
    # Get ROS parameters (configurable via launch file)
    bag_path = rospy.get_param("/bag_file", os.path.join(PARENT_DIR, "data/assignment.bag"))
    image_topic = rospy.get_param("/image_topic", "/hikcamera/image_2/compressed")
    rospy.loginfo(f"[Detection] Starting UAS vehicle detection (ROS Noetic)")
    rospy.loginfo(f"[Detection] Rosbag path: {bag_path}")
    rospy.loginfo(f"[Detection] Image topic: {image_topic}")

    try:
        # Open rosbag
        bag = rosbag.Bag(bag_path, "r")
        frame_num = 0

        # Iterate over rosbag messages (CompressedImage)
        for topic, msg, t in bag.read_messages(topics=[image_topic]):
            # Exit if ROS node is shutdown
            if rospy.is_shutdown():
                break

            # Convert ROS CompressedImage to OpenCV (适配/hikcamera/image_2/compressed)
            try:
                # Parse compressed data to numpy array
                np_arr = np.frombuffer(msg.data, np.uint8)
                # Decode to OpenCV BGR image (Noetic compatible)
                cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            except Exception as e:
                rospy.logerr(f"[Detection] Frame {frame_num} conversion error: {str(e)}")
                continue

            # Process image (detection + annotation + publish)
            annotated_img = process_image(cv_img, frame_num)

            # Show OpenCV window (real-time visualization)
            cv2.imshow("AAE4011 UAS Vehicle Detection (ROS Noetic)", annotated_img)

            # Exit on 'q' key press (1ms delay for real-time playback)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                rospy.loginfo("[Detection] Exit requested (q key pressed)")
                break

            frame_num += 1

        # Cleanup (Noetic resource release)
        bag.close()
        cv2.destroyAllWindows()
        rospy.loginfo(f"[Detection] Completed! Processed {frame_num} frames")

    except FileNotFoundError:
        rospy.logfatal(f"[Detection] Rosbag not found: {bag_path}")
    except Exception as e:
        rospy.logfatal(f"[Detection] Fatal error: {str(e)}")

if __name__ == "__main__":
    # Initialize ROS node (Noetic)
    rospy.init_node("uas_vehicle_detection_node_noetic", anonymous=True)
    # Initialize ROS publisher (/detect/result_image for RQT)
    detect_pub = rospy.Publisher("/detect/result_image", Image, queue_size=10)
    # Run real-time detection
    try:
        real_time_detection()
    except rospy.ROSInterruptException:
        rospy.loginfo("[Detection] ROS node interrupted")
    finally:
        # Ensure OpenCV windows are closed (Noetic fix)
        cv2.destroyAllWindows()

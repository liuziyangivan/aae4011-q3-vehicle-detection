#!/usr/bin/env python3
"""
ROS Noetic Rosbag Image Extractor (Ubuntu 20.04)
AAE4011 Q3 - UAS Vehicle Detection
Core Functions:
1. Read ROS bag file with sensor_msgs/CompressedImage topic
2. Convert ROS CompressedImage to OpenCV BGR (Python3 compatible)
3. Save all frames to local directory
4. Report frame count, resolution, FPS and encoding (assignment requirement)
"""
import rospy
import rosbag
import cv2
import os
import numpy as np  # For CompressedImage decoding
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CompressedImage

# Initialize CVBridge (Noetic Python3 compatible)
bridge = CvBridge()
# Set default paths (relative to script, easy for ROS launch)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(SCRIPT_DIR, "..")

def extract_frames():
    """Main extraction function with ROS parameter support"""
    # Get ROS parameters (configurable via launch file)
    bag_path = rospy.get_param("/bag_file", os.path.join(PARENT_DIR, "data/assignment.bag"))
    image_topic = rospy.get_param("/image_topic", "/hikcamera/image_2/compressed")
    save_dir = os.path.join(PARENT_DIR, "data/extracted_frames")
    
    # Create save directory if not exists
    os.makedirs(save_dir, exist_ok=True)
    rospy.loginfo(f"[Extractor] Save directory: {save_dir}")

    try:
        # Open rosbag in read mode
        bag = rosbag.Bag(bag_path, "r")
        rospy.loginfo(f"[Extractor] Opened rosbag successfully: {bag_path}")
        frame_count = 0
        img_res = None
        start_time = None
        end_time = None

        # Iterate over all CompressedImage messages in the specified topic
        for topic, msg, t in bag.read_messages(topics=[image_topic]):
            # Record start/end time for FPS calculation
            if start_time is None:
                start_time = t.to_sec()
            end_time = t.to_sec()

            # Convert ROS CompressedImage to OpenCV (适配/hikcamera/image_2/compressed)
            try:
                # Parse compressed data to numpy array
                np_arr = np.frombuffer(msg.data, np.uint8)
                # Decode to OpenCV BGR image (Noetic compatible)
                cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            except Exception as e:
                rospy.logerr(f"[Extractor] Frame {frame_count} conversion error: {str(e)}")
                continue

            # Record image resolution (width x height) - only once
            if img_res is None:
                img_res = (cv_img.shape[1], cv_img.shape[0])

            # Save frame with 4-digit numbering (frame_0000.jpg)
            frame_name = f"frame_{frame_count:04d}.jpg"
            cv2.imwrite(os.path.join(save_dir, frame_name), cv_img)
            frame_count += 1

            # Log progress every 50 frames (avoid terminal spam)
            if frame_count % 50 == 0:
                rospy.loginfo(f"[Extractor] Extracted {frame_count} frames...")

        # Calculate key metrics (assignment requirement)
        bag_duration = end_time - start_time if (end_time and start_time) else 0
        avg_fps = frame_count / bag_duration if bag_duration > 0 else 0

        # Print final report (MANDATORY for assignment criterion)
        rospy.loginfo("="*60)
        rospy.loginfo("[Extractor] Rosbag Image Extraction Report (AAE4011 Q3)")
        rospy.loginfo("="*60)
        rospy.loginfo(f"Total Frames Extracted: {frame_count}")
        rospy.loginfo(f"Image Resolution (W x H): {img_res}")
        rospy.loginfo(f"Rosbag Duration: {bag_duration:.2f} seconds")
        rospy.loginfo(f"Average FPS: {avg_fps:.2f}")
        rospy.loginfo(f"Image Type: CompressedImage (hikcamera)")
        rospy.loginfo(f"Frames Saved To: {save_dir}")
        rospy.loginfo("="*60)

        # Close bag to release resources
        bag.close()
        rospy.loginfo("[Extractor] Extraction completed successfully!")

    except FileNotFoundError:
        rospy.logfatal(f"[Extractor] Rosbag file not found: {bag_path}")
        return
    except Exception as e:
        rospy.logfatal(f"[Extractor] Fatal error: {str(e)}")
        return

if __name__ == "__main__":
    # Initialize ROS node (anonymous=True for unique name)
    rospy.init_node("rosbag_image_extractor_noetic", anonymous=True)
    # Run extraction function
    extract_frames()
    # Shutdown ROS node
    rospy.signal_shutdown("Extraction finished")

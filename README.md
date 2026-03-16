# AAE4011 Assignment 1 Q3: UAS Vehicle Detection from Rosbag
ROS Noetic (Ubuntu 20.04 LTS) based real-time vehicle detection for Unmanned Aerial Systems (UAS) using YOLOv8 nano. This project parses `sensor_msgs/CompressedImage` from rosbag topic `/hikcamera/image_2/compressed`, extracts frames, and detects vehicles (Car/Bus/Truck) with annotated bounding boxes/labels/confidence scores.

## Author
- Name: LIU Ziyang
- PolyU ID: 22100364D
- Email: 22100364D@connect.polyu.hk
- Course: AAE4011 (Unmanned Aerial Systems)

## Project Overview
### Core Objectives
- Extract frames from ROS compressed image rosbag and report key metrics (frame count, resolution, FPS).
- Implement real-time vehicle detection with lightweight YOLOv8 nano (UAS-friendly).
- Visualize results via OpenCV window and ROS RQT image viewer.

### Technical Stack
- OS: Ubuntu 20.04 LTS
- ROS Version: Noetic
- Detection Model: YOLOv8 nano (ultralytics)
- Image Topic: `/hikcamera/image_2/compressed` (sensor_msgs/CompressedImage)
- Language: Python 3.8 (ROS Noetic default)

## Project File Structure
   ```plaintext
   uas_vehicle_detect/
   ├── launch/
   │   └── vehicle_detect.launch
   ├── scripts/
   │   ├── rosbag_extract.py
   │   └── detect_node.py
   ├── config/
   ├── data/
   │   ├── assignment.bag
   │   └── extracted_frames/
   ├── results/
   ├── package.xml
   ├── CMakeLists.txt
   ├── requirements.txt
   ├── .gitignore
   └── README.md
   ```

## Environment Setup
### Prerequisites (Ubuntu 20.04 Only)
1. Install ROS Noetic (if not installed):
   ```bash
   sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
   sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
   sudo apt update && sudo apt install ros-noetic-desktop-full -y
   echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
   source ~/.bashrc
2. Install ROS/Python dependencies:
   ```bash
   sudo apt install ros-noetic-cv-bridge ros-noetic-image-transport ros-noetic-rosbag ros-noetic-rqt-image-view python3-catkin-tools -y
   pip3 install torch==2.0.1 torchvision==0.15.2 ultralytics==8.0.200 opencv-python==4.8.1.78 numpy==1.24.4
3. Build ROS Workspace:
   ```bash
   mkdir -p ~/aae4011_ws/src
   cd ~/aae4011_ws/src
   git clone https://github.com/liuziyangivan/aae4011-q3-vehicle-detection.git
   cd ~/aae4011_ws
   catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python3
   source devel/setup.bash

## Step-by-Step Execution
1. Prepare Rosbag File:
   ```bash
   cp /path/to/your/rosbag.bag ~/aae4011_ws/src/uas_vehicle_detect/data/assignment.bag
   ls ~/aae4011_ws/src/uas_vehicle_detect/data/
2. Extract Frames from Rosbag:
   ```bash
   roscore &
   cd ~/aae4011_ws
   source devel/setup.bash
   rosrun uas_vehicle_detect rosbag_extract.py
- Extracted frames are saved to data/extracted_frames/;
- A report (frame count/resolution/FPS) will be printed in terminal.
3. Run Real-Time Vehicle Detection:
   ```bash
   cd ~/aae4011_ws
   source devel/setup.bash
   roslaunch uas_vehicle_detect vehicle_detect.launch
- An OpenCV window will pop up with real-time detection results;
- Red bounding boxes = vehicles, white labels = class + confidence (e.g., Car: 0.92);
- Green text (bottom-left) = frame count + detected vehicle number.
4. Visualize with ROS RQT (Official Tool):
   ```bash
   source ~/aae4011_ws/devel/setup.bash
   rqt_image_view /detect/result_image
5. Exit
- Press q in the OpenCV window to stop detection;
- Stop ROS Master: kill %1 (if started with roscore &).

## Method Description
Detection Pipeline
1. Rosbag Parsing: Read sensor_msgs/CompressedImage from rosbag topic /hikcamera/image_2/compressed (non-standard Image topic, requires special decoding).
2. Image Decoding: Convert compressed image data to OpenCV BGR format using numpy.frombuffer + cv2.imdecode (ROS Noetic compatible).
3. YOLOv8 Inference: Run YOLOv8 nano model to detect only vehicle classes (Car/Bus/Truck) with:
-Confidence threshold: 0.25 (filter low-confidence detections);
-IOU threshold: 0.45 (avoid duplicate bounding boxes via NMS).
4. Result Annotation: Draw red bounding boxes, white class labels (with confidence scores), and green statistics on images.
5. Visualization: Publish annotated images to ROS topic /detect/result_image (for RQT) and display in OpenCV window.

## Why YOLOv8 Nano?
- Lightweight: 6MB model size (ideal for UAS with limited compute resources);
- Real-Time: >30 FPS on Ubuntu 20.04 (meets UAS real-time requirements);
- Pre-trained: COCO dataset pre-training supports vehicle detection out-of-the-box (no manual training);
- Efficient: Built-in NMS reduces redundant detections for accurate results.

## Important Notes
1. Rosbag Topic Check: Ensure the image topic in launch/vehicle_detect.launch matches your rosbag (current: /hikcamera/image_2/compressed). Check via:
   ```bash
   rosbag info ~/aae4011_ws/src/uas_vehicle_detect/data/assignment.bag
2. YOLOv8 Model Download: If yolov8n.pt fails to download automatically, manually download it to ~/.ultralytics/models/ from https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt.
3. Indentation Errors: All Python scripts use 4 spaces for indentation (no tabs) to avoid TabError.
4. Rosbag Size: Rosbag files are excluded from Git (via .gitignore) due to large size – share the rosbag separately if needed.

## Video Demonstration
Video demo link: 

## Reflection and Critical Analysis
(a) What I learned
1. Technical skills: Mastered rosbag data parsing (extracting image messages from rosbag files) and cv_bridge conversion between ROS sensor_msgs/Image and OpenCV image formats, which are foundational for UAS perception development.
2. Integration ability: Learned to embed a lightweight deep learning model (YOLOv8n) into a ROS node, realizing real-time data flow from camera input to detection output in a robotic system.

(b) AI tool usage
1. AI generated ROS template code and debugged errors, greatly speeding up my development.
2. AI helped me learn Ubuntu and ROS efficiently. It explained concepts clearly, provided step-by-step commands, and solved environment errors.

Benefit: Accelerated coding process. AI assistants quickly generated boilerplate code for ROS subscribers/publishers and YOLO model integration, reducing time spent on syntax debugging.

Limitation: Syntax incompatibility. AI occasionally generated ROS 1/ROS 2 mixed syntax, requiring manual verification and correction for the target ROS version (Noetic/Humble).

(c) Accuracy improvement
1. Image preprocessing: Add Gaussian denoising and contrast enhancement to input frames to reduce interference from drone vibration and varying lighting conditions.
2. Post-processing optimization: Implement non-maximum suppression (NMS) with adjusted IoU thresholds to eliminate redundant bounding boxes for overlapping vehicles.

(d) Real-world challenges
1. Computational constraints: UAS onboard computers (e.g., Raspberry Pi, Jetson Nano) have limited CPU/GPU resources, leading to inference latency if using non-lightweight models.
2. Environmental interference: Motion blur (from fast UAS flight) and occlusions (e.g., trees, buildings) reduce detection stability and increase false negative rates.

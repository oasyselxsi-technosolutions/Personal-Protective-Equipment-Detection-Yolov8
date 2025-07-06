
# Personal Protective Equipment Detection using YOLOv8

![Project Logo](https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/blob/master/static/images/1.jpg?raw=true)

## Table of Contents
1. Introduction
2. Prerequisites
3. Installation
4. Usage
5. Model Architecture (YOLOv8)
6. Dataset
7. Training
8. Evaluation
9. Results
10. Deployment with Flask
11. Future Improvements


## 1. Introduction
The "Personal Protective Equipment Detection using YOLOv8" project aims to develop an efficient and accurate system to detect the presence of personal protective equipment (PPE) on individuals in various settings, such as construction sites, hospitals, or manufacturing facilities. The system utilizes the YOLOv8 object detection model, leveraging machine learning and computer vision techniques to automatically identify whether a person is wearing appropriate PPE, including items like helmets, masks, and safety vests.

## 2. Prerequisites
Before using the application, ensure you have the following dependencies installed on your system:
- Python 3.6+
- Flask
- OpenCV
- Pytorch
- NumPy
- Matplotlib

## 3. Installation
To set up the project on your local machine, follow these steps:
1. Clone the repository to your local machine using the following command:

```https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/```


2. Change into the project directory:
```
cd your-repo
```

3. Install the required Python packages using pip:
```pip install -r requirements.txt```

4. Set up environment variables:
```
copy .env.example .env
```
Edit the `.env` file with your camera credentials and configuration:
```
CAMERA_IP=your_camera_ip_address
CAMERA_USERNAME=your_camera_username  
CAMERA_PASSWORD=your_camera_password
CAMERA_PORT=554
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True
```


## 4. Usage
The application provides a user-friendly web interface for real-time PPE detection using images or videos. To use the application:

- Run the Flask app using the following command:
```python flaskapp.py ```

- Open your web browser and navigate to `http://localhost:5000`.
- Upload an image or provide a link to a video for PPE detection.
- Click the "Detect PPE" button to initiate the detection process.
- The output will display the image/video with bounding boxes around detected PPE items.

## 5. Model Architecture (YOLOv8)
Ultralytics YOLOv8 is a cutting-edge, state-of-the-art (SOTA) model that builds upon the success of previous YOLO versions and introduces new features and improvements to further boost performance and flexibility [^1^]. YOLOv8 is designed to be fast, accurate, and easy to use, making it an excellent choice for a wide range of object detection and tracking, instance segmentation, image classification, and pose estimation tasks [^1^].

[^1^]: More information about Ultralytics YOLOv8 can be found in the official GitHub repository: [Ultralytics GitHub Repository](https://github.com/ultralytics/ultralytics).

## 6. Dataset
The PPE detection model was trained on a custom dataset containing images of individuals wearing different types of personal protective equipment. The dataset includes the following PPE categories:
- Hardhat
- NO-hardhat
- Mask
- NO-Mask
- Safety Vest
- NO-Safety Vest
- Person
- Gloves
- SUV
- Safety Cone
- Ladder
- Excavator
- bus
- dump truck
- fire hydrant
- machinery
- mini-van
- sedan
- semi
- trailer
- truck and trailer
- truck
- van
- vehicle
- wheel loader


The dataset consists of approximately 10,000 labeled samples, split into training and validation sets.

## 7. Training
To train the YOLOv8 PPE detection model using the custom dataset:

- Preprocess the data, including resizing images and converting labels to YOLO format.
- Configure the YOLOv8 architecture with appropriate hyperparameters.
- Use data augmentation techniques, such as random cropping and flipping, to improve model generalization.
- Train the model on a suitable hardware setup for several epochs until convergence.

## 8. Evaluation
The model's performance was evaluated using several evaluation metrics, including:
- Precision
![Precision Curve](https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/blob/master/120_V8n/P_curve.png?raw=true)
- Recall
![Recall Curve](https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/blob/master/120_V8n/R_curve.png?raw=true)
- F1 Score
![F1 Confidence Curve](https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/blob/master/120_V8n/F1_curve.png?raw=true)


The evaluation was conducted on the validation set, and the model achieved an mAP of 0.85 for PPE detection.

## 9. Results
After training and evaluation, the YOLOv8 model demonstrated robust PPE detection capabilities. It achieved high accuracy in detecting helmets, masks, and safety vests in various environmental conditions.

Here is a visualization of the detection results on sample images:

![Sample Detection](https://github.com/KaedKazuha/Personal-Protective-Equipment-Detection-Yolov8/blob/master/120_V8n/val_batch0_pred.jpg?raw=true)


## 10. Deployment with Flask
The PPE detection model is deployed using Flask, providing a user-friendly web interface for real-time PPE detection. Flask enables seamless integration with the model, allowing users to upload images or provide links to videos and receive instant detection results through the web app.

### Development Mode (Local Testing)
```bash
python flaskapp.py
```
Access at: `http://localhost:5000`

### Production Mode (Local Network Access)

#### Option 1: Basic Production Mode
```cmd
# Windows
run_flask_production.bat

# Or manually set environment and run
set FLASK_DEBUG=False
set FLASK_ENV=production
python flaskapp.py
```

#### Option 2: Waitress Production Server (Recommended for Windows)
```cmd
# Install production dependencies
pip install waitress gunicorn

# Start with Waitress (production-grade WSGI server)
waitress-serve --host=0.0.0.0 --port=5000 --threads=8 wsgi:app
```

#### Option 3: Automated Production Setup
```cmd
# Windows - Automated setup and run
run_production_waitress.bat
```

### Network Access Configuration

#### Local Network Access
- **Development**: `http://127.0.0.1:5000` (local machine only)
- **Production**: `http://192.168.8.219:5000` (accessible from all devices on local network)

#### Available Endpoints
Once running, the application provides these endpoints:
- **Main Application**: `http://192.168.8.219:5000`
- **Camera Debug Interface**: `http://192.168.8.219:5000/camera_debug`
- **IP Camera (YOLO Detection)**: `http://192.168.8.219:5000/ipcamera`
- **IP Camera (Raw Stream)**: `http://192.168.8.219:5000/ipcamera_raw`
- **Stable Endpoints**: `http://192.168.8.219:5000/ipcamera_stable`
- **Adaptive Endpoints**: `http://192.168.8.219:5000/ipcamera_adaptive`
- **Webcam Stream**: `http://192.168.8.219:5000/webapp`

#### Environment Configuration for Production
Update your `.env` file for production deployment:
```properties
# Camera Configuration
CAMERA_IP=192.168.8.210
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_camera_password
CAMERA_PORT=554

# Camera Settings
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_BUFFER_SIZE=1

# Flask Configuration (Production)
FLASK_SECRET_KEY=your-very-secure-secret-key-change-this
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_DEBUG=False
```

#### Windows Firewall Configuration
To allow network access, add a firewall rule (run as Administrator):
```cmd
netsh advfirewall firewall add rule name="Python Flask App" dir=in action=allow protocol=TCP localport=5000
```

#### Testing Network Access
1. **Test camera connection**: Visit `http://192.168.8.219:5000/camera_debug`
2. **Mobile device access**: Connect phone/tablet to same WiFi, open browser to the above URL
3. **Other computers**: Any device on the same network (192.168.8.x) can access the application

#### Camera Endpoint Types
- **Standard**: Basic camera streaming with YOLO detection
- **Stable**: Enhanced stability with buffer management for unreliable connections
- **Adaptive**: Optimized for high-resolution cameras with dynamic frame processing
- **Raw**: Direct camera stream without YOLO processing (faster performance)

### Production vs Development Mode

| Feature | Development Mode | Production Mode |
|---------|------------------|-----------------|
| **Debug** | ✅ Enabled | ❌ Disabled |
| **Auto-reload** | ✅ Yes | ❌ No |
| **Error Details** | ✅ Full Stack | ❌ Generic |
| **Performance** | ⚠️ Slower | ✅ Optimized |
| **Network Access** | ⚠️ Local Only | ✅ Local Network |
| **Security** | ⚠️ Lower | ✅ Higher |

### Additional Documentation
- `PRODUCTION_DEPLOYMENT.md` - Complete production deployment guide
- `NETWORK_SETUP.md` - Network configuration and troubleshooting
- `EXTERNAL_ACCESS_GUIDE.md` - Making the app available over the internet
- `ENVIRONMENT_SETUP.md` - Detailed environment variable configuration

## 11. Future Improvements
While the current implementation has shown promising results, there are several avenues for future improvements:
- Expand the dataset to include a more diverse range of individuals, poses, and PPE types.
- Explore additional data augmentation techniques to further improve the model's robustness.
- Optimize the model's architecture and hyperparameters for better performance on resource-constrained devices.






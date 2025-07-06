# IP Camera and Webcam Route Verification & Fixes

## Issues Found and Fixed

### 1. IP Camera Route (`/ipcamera`) Issues
**Problem**: YOLO detection was not being applied to IP camera frames
**Root Cause**: 
- The code was commented out: `# processed_frame = video_detection_single_frame(frame)`
- The `video_detection_single_frame` function didn't exist in YOLO_Video.py

**Fixes Applied**:
- ✅ Created `video_detection_single_frame()` function in `YOLO_Video.py`
- ✅ Updated imports in `flaskapp.py` to include the new function
- ✅ Modified `/ipcamera` route to actually apply YOLO detection
- ✅ Added multiple IP camera URL formats to test connection
- ✅ Improved error handling and connection testing

### 2. Webcam Route (`/webapp`) Issues
**Problem**: Using `video_detection(0)` which was designed for video files, not live streams
**Root Cause**: 
- `video_detection()` includes `cv2.imshow()` and `cv2.waitKey()` which are incompatible with web streaming
- Function expects video file paths, not camera indices

**Fixes Applied**:
- ✅ Created `generate_frames_webcam()` function specifically for webcam streaming
- ✅ Updated `/webapp` route to use the new webcam function
- ✅ Added proper error handling for webcam connection

### 3. Additional Improvements
- ✅ Added `/ipcamera_raw` route for IP camera without YOLO detection (for performance comparison)
- ✅ Created `generate_frames_ip_camera_with_yolo()` with optional YOLO detection
- ✅ Updated camera debug template with multiple stream options
- ✅ Added comprehensive connection testing with multiple URL formats
- ✅ Improved timeout handling for network streams

## Available Routes

### 1. `/ipcamera` - IP Camera with YOLO Detection
- **Purpose**: Stream from IP camera with PPE detection
- **Features**: Full YOLO detection, bounding boxes, safety equipment identification
- **Performance**: Higher CPU usage due to AI processing

### 2. `/ipcamera_raw` - IP Camera without YOLO Detection  
- **Purpose**: Raw IP camera stream for testing connectivity
- **Features**: No AI processing, just raw camera feed
- **Performance**: Low CPU usage, faster streaming

### 3. `/webapp` - Webcam with YOLO Detection
- **Purpose**: Stream from local webcam with PPE detection
- **Features**: Full YOLO detection on webcam feed
- **Performance**: Depends on webcam quality and system performance

### 4. `/camera_debug` - Debug Interface
- **Purpose**: Test and debug camera connections
- **Features**: 
  - Test camera connectivity
  - Switch between different camera sources
  - View connection status and errors

## How to Test

### 1. Basic Testing
```bash
# Start the Flask application
python flaskapp.py

# Open browser and navigate to:
http://127.0.0.1:5000/camera_debug
```

### 2. Test Individual Routes
- **IP Camera with YOLO**: `http://127.0.0.1:5000/ipcamera`
- **IP Camera Raw**: `http://127.0.0.1:5000/ipcamera_raw`  
- **Webcam with YOLO**: `http://127.0.0.1:5000/webapp`
- **Camera Test**: `http://127.0.0.1:5000/test_camera`

### 3. Advanced Testing
```bash
# Run the camera test script
python test_camera.py
```

## IP Camera URL Formats Tested

The system now tests multiple URL formats automatically using environment variables from `.env` file:
1. `rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream`
2. `rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream1`
3. `rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/live`
4. `rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/cam/realmonitor?channel=1&subtype=0`
5. `http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream`
6. `http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}/video.cgi`
7. `http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}/videostream.cgi`
8. `http://{CAMERA_IP}/video.cgi?user={CAMERA_USERNAME}&pwd={CAMERA_PASSWORD}`

**Note**: Camera credentials are now configured via environment variables in `.env` file for security.

## Troubleshooting

### If IP Camera Still Doesn't Work:
1. **Check Network Connectivity**:
   ```bash
   ping {your_camera_ip}
   ```

2. **Verify Camera Web Interface**:
   - Open `http://{your_camera_ip}` in browser
   - Login with your camera credentials

3. **Environment Configuration**:
   - Ensure `.env` file exists with correct camera credentials
   - Copy `.env.example` to `.env` and update with your camera details:
     ```
     CAMERA_IP=your_camera_ip
     CAMERA_USERNAME=your_username
     CAMERA_PASSWORD=your_password
     CAMERA_PORT=554
     ```
4. **Check Camera Settings**:
   - Ensure RTSP/HTTP streaming is enabled
   - Verify correct port numbers
   - Check if camera supports the URL formats being tested

5. **Firewall Issues**:
   - Ensure ports 554 (RTSP) and 80 (HTTP) are open
   - Check Windows Firewall settings

### If Webcam Doesn't Work:
1. **Check Device Manager**: Ensure webcam is recognized
2. **Test with Other Applications**: Try Windows Camera app
3. **Driver Issues**: Update webcam drivers
4. **Permission Issues**: Check camera privacy settings in Windows

### If YOLO Detection Doesn't Work:
1. **Check Model File**: Ensure `YOLO-Weights/bestest.pt` exists
2. **Dependencies**: Verify ultralytics package is installed
3. **GPU Memory**: YOLO detection requires sufficient memory

## Performance Notes

- **YOLO Detection**: Adds ~100-500ms processing time per frame depending on hardware
- **IP Camera**: Network latency may affect streaming quality
- **Webcam**: Local processing is typically faster than IP camera
- **Frame Rate**: System automatically adjusts based on processing capabilities

## Security Considerations

- **Credentials**: Camera credentials are now securely stored in `.env` file (excluded from git)
- **Environment Setup**: Copy `.env.example` to `.env` and configure with your camera details
- **Network**: Ensure camera network is secure
- **Access**: Consider adding authentication to camera routes in production

## Environment Setup

1. **Copy the example environment file**:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` with your camera credentials**:
   ```
   CAMERA_IP=your_camera_ip_address
   CAMERA_USERNAME=your_camera_username
   CAMERA_PASSWORD=your_camera_password
   CAMERA_PORT=554
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   FLASK_DEBUG=True
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

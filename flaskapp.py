from flask import Flask, render_template, Response,jsonify,request,session

from flask_wtf import FlaskForm

from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required to run the YOLOv8 model
import cv2
from flask_cors import CORS

# YOLO_Video is the python file which contains the code for our object detection model
#Video Detection is the Function which performs Object Detection on Input Video
from YOLO_Video import video_detection, video_detection_single_frame
from YOLO_Video import detect_manufacturing_ppe
from ultralytics import YOLO
from config import violation_recording_enabled
import config
# Add near your other imports
from collections import defaultdict
import re
from datetime import datetime


config.violation_recording_enabled = False

# Camera configuration from environment variables
CAMERA_IP = os.getenv('CAMERA_IP', '192.168.8.210')
CAMERA_USERNAME = os.getenv('CAMERA_USERNAME', 'admin')
CAMERA_PASSWORD = os.getenv('CAMERA_PASSWORD', 'defaultpassword')
CAMERA_PORT = os.getenv('CAMERA_PORT', '554')
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '640'))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '480'))
CAMERA_BUFFER_SIZE = int(os.getenv('CAMERA_BUFFER_SIZE', '1'))

# Flask configuration from environment variables
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
# Global variable to hold the webcam capture object
webcam_cap = None
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
# Add at the top
violation_recording_enabled = False

app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/files'

def get_camera_urls():
    """Generate camera URLs using environment variables."""
    base_urls = [
        f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream",
        f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream1",
        f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/live",
        f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/cam/realmonitor?channel=1&subtype=0",
        f"http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream",
        f"http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}/video.cgi",
        f"http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}/videostream.cgi",
        f"http://{CAMERA_IP}/video.cgi?user={CAMERA_USERNAME}&pwd={CAMERA_PASSWORD}"
    ]
    return base_urls

def get_primary_camera_url():
    """Get the primary camera URL for direct access."""
    return f"http://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream"


#Use FlaskForm to get input video file  from user
class UploadFileForm(FlaskForm):
    #We store the uploaded video file path in the FileField in the variable file
    #We have added validators to make sure the user inputs the video in the valid format  and user does upload the
    #video when prompted to do so
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")


def generate_frames(path_x = ''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

# filepath: [flaskapp.py](http://_vscodecontentref_/0)

def generate_frames_ip_camera(ip_camera_url):
    """Generate frames from the IP camera."""
    cap = None
    try:
        print(f"Attempting to connect to IP camera: {ip_camera_url}")
        cap = cv2.VideoCapture(ip_camera_url)
        
        # Set properties to improve connection
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)
        
        # Set timeout for network streams (in milliseconds)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open camera stream: {ip_camera_url}")
            return
        
        print("Camera connection successful, starting frame generation...")
        frame_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        while True:
            success, frame = cap.read()
            if not success:
                consecutive_failures += 1
                print(f"Failed to read frame {frame_count}, consecutive failures: {consecutive_failures}")
                
                if consecutive_failures >= max_consecutive_failures:
                    print(f"Too many consecutive failures ({consecutive_failures}), stopping stream")
                    break
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            frame_count += 1
            
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"Processed {frame_count} frames")
            
            # Apply YOLO detection to the IP camera frame
            try:
                # Apply YOLO detection to the IP camera frame
                processed_frame = video_detection_single_frame(frame)
                
                ref, buffer = cv2.imencode('.jpg', processed_frame)
                if not ref:
                    print("Error encoding frame")
                    continue
                    
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in generate_frames_ip_camera: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Camera released")

@app.route('/ipcamera')
def ipcamera():
    """Route to display IP camera feed."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL: {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            test_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
            
            if test_cap.isOpened():
                # Try to read a frame to confirm it works
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to: {url}")
                    break
                else:
                    print(f"✗ Connected but no frames from: {url}")
            else:
                test_cap.release()
                print(f"✗ Failed to connect to: {url}")
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera with any URL format",
                "tried_urls": camera_urls,
                "suggestions": [
                    "Check if the camera is powered on and connected to network",
                    f"Verify the IP address ({CAMERA_IP}) is correct",
                    f"Check username ({CAMERA_USERNAME}) and password",
                    "Try accessing camera web interface in browser first",
                    "Check if camera supports RTSP or HTTP streaming",
                    f"Verify camera port ({CAMERA_PORT} for RTSP, 80 for HTTP)"
                ]
            }), 500
        
        print(f"Using working camera URL: {working_url}")
        return Response(generate_frames_ip_camera_with_yolo(working_url, apply_yolo=True), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera route: {str(e)}")
        return jsonify({"error": str(e)}), 500        

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')
# Rendering the Webcam Rage
#Now lets make a Webcam page for the application
#Use 'app.route()' method, to render the Webcam page at "/webcam"
@app.route("/webcam", methods=['GET','POST'])

def webcam():
    session.clear()
    return render_template('ui.html')
@app.route('/FrontPage', methods=['GET','POST'])
def front():
    # Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        # Our uploaded video file path is saved here
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file
        # Use session storage to save video file path
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
    return render_template('videoprojectnew.html', form=form)
@app.route('/video')
def video():
    #return Response(generate_frames(path_x='static/files/bikes.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(path_x = session.get('video_path', None)),mimetype='multipart/x-mixed-replace; boundary=frame')

# To display the Output Video on Webcam page
@app.route('/webapp')
def webapp():
    """Route to display webcam feed with YOLO detection."""
    try:
        return Response(generate_frames_webcam(), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webapp route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test_camera')
def test_camera():
    """Test route to check IP camera connectivity."""
    ip_camera_url = get_primary_camera_url()
    
    try:
        print(f"Testing camera connection to: {ip_camera_url}")
        cap = cv2.VideoCapture(ip_camera_url)
        
        if not cap.isOpened():
            cap.release()
            return jsonify({
                "status": "failed",
                "message": "Cannot connect to IP camera",
                "url": ip_camera_url,
                "suggestions": [
                    "Check if the camera is powered on",
                    "Verify the IP address and port",
                    "Check network connectivity",
                    "Verify username and password",
                    "Try accessing the camera URL directly in a browser"
                ]
            })
        
        # Try to read one frame
        success, frame = cap.read()
        cap.release()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Camera connection successful",
                "frame_shape": frame.shape if frame is not None else None
            })
        else:
            return jsonify({
                "status": "failed",
                "message": "Connected to camera but cannot read frames"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
@app.route('/camera_debug')
def camera_debug():
    """Debug page for IP camera testing."""
    return render_template('camera_debug.html')

def generate_frames_ip_camera_with_yolo(ip_camera_url, apply_yolo=True):
    """Generate frames from the IP camera with optional YOLO detection."""
    cap = None
    try:
        print(f"Attempting to connect to IP camera: {ip_camera_url}")
        print(f"YOLO detection: {'Enabled' if apply_yolo else 'Disabled'}")
        cap = cv2.VideoCapture(ip_camera_url)
        
        # Set properties to improve connection
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)
        
        # Set timeout for network streams (in milliseconds)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open camera stream: {ip_camera_url}")
            return
        
        print("Camera connection successful, starting frame generation...")
        frame_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        while True:
            success, frame = cap.read()
            if not success:
                consecutive_failures += 1
                print(f"Failed to read frame {frame_count}, consecutive failures: {consecutive_failures}")
                
                if consecutive_failures >= max_consecutive_failures:
                    print(f"Too many consecutive failures ({consecutive_failures}), stopping stream")
                    break
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            frame_count += 1
            
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"Processed {frame_count} frames")
            
            # Apply YOLO detection if enabled
            try:
                if apply_yolo:
                    processed_frame = video_detection_single_frame(frame)
                else:
                    processed_frame = frame
                
                ref, buffer = cv2.imencode('.jpg', processed_frame)
                if not ref:
                    print("Error encoding frame")
                    continue
                    
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in generate_frames_ip_camera_with_yolo: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Camera released")

@app.route('/ipcamera_raw')
def ipcamera_raw():
    """Route to display raw IP camera feed without YOLO detection."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL (raw): {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to (raw): {url}")
                    break
            else:
                test_cap.release()
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera (raw)"
            }), 500
        
        print(f"Using working camera URL (raw): {working_url}")
        return Response(generate_frames_ip_camera_with_yolo(working_url, apply_yolo=False), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera_raw route: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_frames_webcam():
    """Generate frames from webcam with YOLO detection."""
    cap = None
    try:
        print("Attempting to connect to webcam...")
        cap = cv2.VideoCapture(0)  # Use default webcam
        
        # Set properties
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Webcam connection successful, starting frame generation...")
        frame_count = 0
        
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to read frame from webcam")
                break
            
            frame_count += 1
            
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"Processed {frame_count} webcam frames")
            
            try:
                # Apply YOLO detection to webcam frame
                processed_frame = video_detection_single_frame(frame)
                
                ref, buffer = cv2.imencode('.jpg', processed_frame)
                if not ref:
                    print("Error encoding webcam frame")
                    continue
                    
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error processing webcam frame: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in generate_frames_webcam: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Webcam released")

@app.route('/webcam_feed')
def webcam_feed():
    """Route to display webcam feed with YOLO detection."""
    try:
        return Response(generate_frames_webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_feed route: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_frames_ip_camera_stable(ip_camera_url, apply_yolo=True):
    """Generate frames from IP camera with enhanced stability and corruption prevention."""
    cap = None
    try:
        print(f"Attempting to connect to IP camera (stable): {ip_camera_url}")
        cap = cv2.VideoCapture(ip_camera_url)
        
        # Enhanced camera properties for stability
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer to reduce latency
        
        # Try to set reasonable resolution first
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 10)  # Reduced FPS for stability
        
        # Network timeout settings
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
        
        # Additional stability settings
        try:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        except:
            pass  # Some cameras don't support FOURCC setting
        
        if not cap.isOpened():
            print(f"Error: Could not open camera stream: {ip_camera_url}")
            return
        
        # Check actual resolution after opening
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Camera opened with resolution: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
        
        print("Camera connection successful, starting stable frame generation...")
        frame_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 5
        last_valid_frame = None
        frame_skip_counter = 0
        reconnect_count = 0
        max_reconnects = 3
        
        while True:
            # Clear buffer by reading multiple frames quickly to get the latest frame
            for _ in range(2):  # Skip 2 frames to reduce latency
                cap.grab()
            
            success, frame = cap.retrieve()
            
            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read frame {frame_count}, consecutive failures: {consecutive_failures}")
                
                # Use last valid frame if available during temporary failures
                if last_valid_frame is not None and consecutive_failures < 3:
                    frame = last_valid_frame.copy()
                    success = True
                    print("Using cached frame during temporary failure")
                
                if consecutive_failures >= max_consecutive_failures:
                    print(f"Too many consecutive failures ({consecutive_failures}), attempting reconnection...")
                    cap.release()
                    
                    if reconnect_count < max_reconnects:
                        # Attempt to reconnect
                        import time
                        time.sleep(2)  # Wait before reconnection
                        cap = cv2.VideoCapture(ip_camera_url)
                        
                        # Reapply settings
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_FPS, 10)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                        if cap.isOpened():
                            print(f"Reconnection successful (attempt {reconnect_count + 1})")
                            consecutive_failures = 0
                            reconnect_count += 1
                            continue
                    
                    print("Max reconnection attempts reached or reconnection failed, stopping stream")
                    break
                
                if not success:
                    continue
            
            # Validate frame quality and detect corruption
            if frame is not None and frame.size > 0:
                # Check if frame is corrupted (all black, too bright, or unusual dimensions)
                frame_mean = frame.mean()
                h, w = frame.shape[:2]
                
                # More flexible frame validation criteria
                is_valid_frame = (
                    frame_mean > 5 and frame_mean < 250 and  # Not all black or all white
                    h > 50 and w > 50 and  # Minimum reasonable dimensions
                    h < 4000 and w < 4000 and  # Allow larger resolutions (up to 4K)
                    len(frame.shape) == 3  # Ensure it's a color frame
                )
                
                if is_valid_frame:
                    # Resize frame if it's too large for processing
                    if h > 1080 or w > 1920:  # If larger than 1080p
                        # Calculate aspect ratio and resize
                        aspect_ratio = w / h
                        if aspect_ratio > 1:  # Landscape
                            new_w = 1280
                            new_h = int(new_w / aspect_ratio)
                        else:  # Portrait or square
                            new_h = 720
                            new_w = int(new_h * aspect_ratio)
                        
                        frame = cv2.resize(frame, (new_w, new_h))
                        print(f"Resized frame from {w}x{h} to {new_w}x{new_h}")
                    
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                    reconnect_count = 0  # Reset reconnect counter on success
                else:
                    print(f"Detected corrupted frame (mean: {frame_mean:.2f}, size: {h}x{w}), using cached frame...")
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                print("Invalid frame detected, skipping...")
                continue
            
            frame_count += 1
            
            # Frame rate control - process every Nth frame to reduce load
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:  # Process every 2nd frame
                continue
            
            if frame_count % 50 == 0:  # Log every 50 processed frames
                print(f"Processed {frame_count} stable frames (failures: {consecutive_failures})")
            
            try:
                if apply_yolo:
                    # Resize frame for YOLO processing if it's too large
                    h, w = frame.shape[:2]
                    if h > 720 or w > 1280:
                        # Resize to a more manageable size for YOLO
                        yolo_frame = cv2.resize(frame, (1280, 720))
                        processed_frame = video_detection_single_frame(yolo_frame)
                        # Resize back to original size if needed
                        processed_frame = cv2.resize(processed_frame, (w, h))
                    else:
                        processed_frame = video_detection_single_frame(frame)
                else:
                    processed_frame = frame
                
                # Enhanced JPEG encoding for better quality and stability
                # Adjust quality based on frame size
                h, w = processed_frame.shape[:2]
                if h * w > 1920 * 1080:  # If larger than 1080p
                    quality = 60  # Lower quality for large frames
                else:
                    quality = 80  # Higher quality for smaller frames
                
                encode_params = [
                    cv2.IMWRITE_JPEG_QUALITY, quality,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1   # Optimize for size
                ]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)
                
                if not ref or buffer is None or len(buffer) == 0:
                    print("Error encoding frame, skipping...")
                    continue
                    
                frame_bytes = buffer.tobytes()
                
                # Ensure frame is properly formatted
                if len(frame_bytes) > 100:  # Minimum size check
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    print("Frame too small, skipping...")
                    continue
                       
            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in generate_frames_ip_camera_stable: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Stable camera released")

def generate_frames_ip_camera_adaptive(ip_camera_url, apply_yolo=True):
    """Generate frames from IP camera with adaptive resolution handling for high-res cameras."""
    cap = None
    try:
        print(f"Attempting to connect to IP camera (adaptive): {ip_camera_url}")
        cap = cv2.VideoCapture(ip_camera_url)
        
        # Start with minimal settings and let camera use its native resolution
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 10)
        
        # Network timeout settings
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera stream: {ip_camera_url}")
            return
        
        # Get camera's native resolution
        native_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        native_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        native_fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Camera native resolution: {native_width}x{native_height} @ {native_fps:.1f}fps")
        
        # Determine optimal streaming resolution
        if native_width > 1920 or native_height > 1080:
            # Calculate aspect ratio and target resolution
            aspect_ratio = native_width / native_height
            if aspect_ratio > 1.7:  # Wide aspect ratio
                target_width = 1280
                target_height = int(target_width / aspect_ratio)
            else:
                target_height = 720
                target_width = int(target_height * aspect_ratio)
            
            print(f"Will resize frames from {native_width}x{native_height} to {target_width}x{target_height}")
        else:
            target_width = native_width
            target_height = native_height
            print("Using native resolution for streaming")
        
        print("Camera connection successful, starting adaptive frame generation...")
        frame_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 10
        last_valid_frame = None
        frame_skip_counter = 0
        reconnect_count = 0
        max_reconnects = 5
        processing_time_sum = 0
        
        import time
        
        while True:
            start_time = time.time()
            
            # Clear buffer by reading multiple frames
            for _ in range(2):
                cap.grab()
            
            success, frame = cap.retrieve()
            
            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read adaptive frame {frame_count}, consecutive failures: {consecutive_failures}")
                
                # Use cached frame during temporary failures
                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True
                    print("Using cached frame during adaptive failure")
                
                if consecutive_failures >= max_consecutive_failures:
                    print(f"Too many consecutive failures ({consecutive_failures}), attempting reconnection...")
                    cap.release()
                    
                    if reconnect_count < max_reconnects:
                        time.sleep(3)  # Wait before reconnection
                        cap = cv2.VideoCapture(ip_camera_url)
                        
                        # Reapply minimal settings
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_FPS, 10)
                        
                        if cap.isOpened():
                            print(f"Adaptive reconnection successful (attempt {reconnect_count + 1})")
                            consecutive_failures = 0
                            reconnect_count += 1
                            continue
                    
                    print("Max adaptive reconnection attempts reached, stopping stream")
                    break
                
                if not success:
                    continue
            
            # Enhanced frame validation for high-resolution cameras
            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]
                
                # Very flexible validation for high-res cameras (supports up to 4K and beyond)
                is_valid_frame = (
                    frame_mean > 3 and frame_mean < 252 and  # Allow wider brightness range
                    h > 100 and w > 100 and  # Minimum dimensions
                    h < 5000 and w < 8000 and  # Support ultra-high resolutions
                    len(frame.shape) == 3  # Color frame
                )
                
                if is_valid_frame:
                    # Adaptive resizing based on resolution
                    if h > target_height or w > target_width:
                        # Resize maintaining aspect ratio
                        aspect_ratio = w / h
                        if aspect_ratio > 1:  # Landscape
                            new_w = target_width
                            new_h = int(new_w / aspect_ratio)
                        else:  # Portrait or square
                            new_h = target_height
                            new_w = int(new_h * aspect_ratio)
                        
                        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                        if frame_count % 100 == 0:  # Log occasionally
                            print(f"Adaptive resize: {w}x{h} -> {new_w}x{new_h}")
                    
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                    reconnect_count = 0
                else:
                    print(f"Detected corrupted adaptive frame (mean: {frame_mean:.2f}, size: {h}x{w})")
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                print("Invalid adaptive frame detected, skipping...")
                continue
            
            frame_count += 1
            
            # Adaptive frame rate control based on processing time
            frame_skip_counter += 1
            avg_processing_time = processing_time_sum / max(frame_count, 1)
            
            # Dynamically adjust frame skipping based on performance
            if avg_processing_time > 0.2:  # If processing is slow
                skip_rate = 3  # Skip more frames
            elif avg_processing_time > 0.1:
                skip_rate = 2
            else:
                skip_rate = 1  # Process all frames if fast enough
            
            if frame_skip_counter % skip_rate != 0:
                continue
            
            if frame_count % 100 == 0:
                print(f"Processed {frame_count} adaptive frames (avg: {avg_processing_time:.3f}s, skip: {skip_rate})")
            
            try:
                if apply_yolo:
                    # Additional resizing for YOLO if frame is still large
                    h, w = frame.shape[:2]
                    if h > 720 or w > 1280:
                        yolo_frame = cv2.resize(frame, (1280, 720))
                        processed_frame = video_detection_single_frame(yolo_frame)
                        # Resize back if needed
                        processed_frame = cv2.resize(processed_frame, (w, h))
                    else:
                        processed_frame = video_detection_single_frame(frame)
                else:
                    processed_frame = frame
                
                # Adaptive quality encoding based on frame size and performance
                h, w = processed_frame.shape[:2]
                if h * w > 1920 * 1080:  # 1080p+
                    quality = 50
                elif h * w > 1280 * 720:  # 720p+
                    quality = 70
                else:
                    quality = 80
                
                encode_params = [
                    cv2.IMWRITE_JPEG_QUALITY, quality,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1
                ]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)
                
                if ref and buffer is not None and len(buffer) > 100:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    continue
                       
            except Exception as e:
                print(f"Error processing adaptive frame: {str(e)}")
                continue
            
            # Track processing time
            processing_time = time.time() - start_time
            processing_time_sum += processing_time
                
    except Exception as e:
        print(f"Error in generate_frames_ip_camera_adaptive: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Adaptive camera released")

@app.route('/ipcamera_stable')
def ipcamera_stable():
    """Route to display stable IP camera feed with YOLO detection."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL (stable): {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to (stable): {url}")
                    break
            else:
                test_cap.release()
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera (stable)"
            }), 500
        
        print(f"Using working camera URL (stable): {working_url}")
        return Response(generate_frames_ip_camera_stable(working_url, apply_yolo=True), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera_stable route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ipcamera_stable_raw')
def ipcamera_stable_raw():
    """Route to display stable IP camera feed without YOLO detection."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL (stable raw): {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to (stable raw): {url}")
                    break
            else:
                test_cap.release()
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera (stable raw)"
            }), 500
        
        print(f"Using working camera URL (stable raw): {working_url}")
        return Response(generate_frames_ip_camera_stable(working_url, apply_yolo=False), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera_stable_raw route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ipcamera_adaptive')
def ipcamera_adaptive():
    """Route to display adaptive IP camera feed with YOLO detection (handles high-res cameras)."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL (adaptive): {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to (adaptive): {url}")
                    break
            else:
                test_cap.release()
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera (adaptive)"
            }), 500
        
        print(f"Using working camera URL (adaptive): {working_url}")
        return Response(generate_frames_ip_camera_adaptive(working_url, apply_yolo=True), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera_adaptive route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ipcamera_adaptive_raw')
def ipcamera_adaptive_raw():
    """Route to display adaptive IP camera feed without YOLO detection (handles high-res cameras)."""
    try:
        # Get camera URLs from environment variables
        camera_urls = get_camera_urls()
        
        working_url = None
        
        # Try each URL format
        for url in camera_urls:
            print(f"Testing camera URL (adaptive raw): {url}")
            test_cap = cv2.VideoCapture(url)
            test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                if ret and frame is not None:
                    working_url = url
                    print(f"✓ Successfully connected to (adaptive raw): {url}")
                    break
            else:
                test_cap.release()
        
        if not working_url:
            return jsonify({
                "error": "Cannot connect to IP camera (adaptive raw)"
            }), 500
        
        print(f"Using working camera URL (adaptive raw): {working_url}")
        return Response(generate_frames_ip_camera_adaptive(working_url, apply_yolo=False), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in ipcamera_adaptive_raw route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/webapp_stable')
def webapp_stable():
    """Route to display stable webcam feed with YOLO detection."""
    try:
        return Response(generate_frames_webcam_stable(), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webapp_stable route: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_frames_webcam_stable():
    """Generate frames from webcam with enhanced stability."""
    cap = None
    try:
        print("Attempting to connect to webcam (stable)...")
        cap = cv2.VideoCapture(0)  # Use default webcam
        
        # Enhanced webcam properties
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Webcam connection successful, starting stable frame generation...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0
        
        while True:
            # Clear buffer for webcam as well
            cap.grab()
            success, frame = cap.retrieve()
            
            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")
                
                # Use cached frame during failures
                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True
                
                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream")
                    break
                
                if not success:
                    continue
            # Validate webcam frame
            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]
                
                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue
            
            frame_count += 1
            
            # Frame rate control
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:  # Process every 2nd frame
                continue
            
            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames")
            
            try:
                # Apply YOLO detection to webcam frame
                processed_frame = video_detection_single_frame(frame)
                
                # Enhanced encoding
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)
                
                if not ref or buffer is None:
                    continue
                    
                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error processing webcam frame: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in generate_frames_webcam_stable: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
            print("Stable webcam released")

@app.route('/api/dashboard')
def dashboard():
    print("[DEBUG] /api/dashboard endpoint called")
    # Example dummy data
    return jsonify({
        "overall_compliance": 70,
        "ppe_compliance": {
            "Helmet": 50,
            "Boots": 88,
            "Glasses": 72,
            "Mask": 45,
            "Gloves": 80
        },
        "ppe_alerts": {
            "Helmet": 40,
            "Boots": 20,
            "Glasses": 72,
            "Mask": 30,
            "Gloves": 10
        },
        "alerts": [34, 32, 41, 85, 88, 60],
        "violation_over_time": [10, 20, 30, 40, 50, 60, 55, 45, 35, 25]
    })


import time
def generate_frames_webcam_raw():
    """Generate frames from webcam without YOLO detection, using global webcam_cap."""
    global webcam_cap
    max_retries = 5
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam (raw) connection successful, starting frame generation...")
            break
        else:
            print(f"Error: Could not open webcam (raw) (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam (raw) after retries.")
        return

    try:
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 30)

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam (raw) after setup")
            return

        print("Webcam (raw) connection confirmed, starting frame generation...")
        frame_count = 0

        while True:
            success, frame = webcam_cap.read()
            if not success:
                print("Failed to read frame from webcam (raw)")
                break

            frame_count += 1

            if frame_count % 30 == 0:
                print(f"Processed {frame_count} webcam (raw) frames")

            try:
                ref, buffer = cv2.imencode('.jpg', frame)
                if not ref:
                    print("Error encoding webcam (raw) frame")
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam (raw) frame: {str(e)}")
                continue

    except Exception as e:
        print(f"Error in generate_frames_webcam_raw: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            webcam_cap = None
            print("Webcam (raw) released")

def api_generate_frames_webcam_yolo():
    """Generate frames from webcam with enhanced stability."""
    global webcam_cap
    max_retries = 15
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam connection successful, starting frame generation...")
            break
        else:
            print(f"Error: Could not open webcam (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam after retries.")
        return

    try:
        print("Attempting to connect to webcam (stable)...")
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam")
            return

        print("Webcam connection successful, starting stable frame generation...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0

        while True:
            webcam_cap.grab()
            success, frame = webcam_cap.retrieve()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")

                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True

                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream")
                    break

                if not success:
                    continue

            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]

                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue

            frame_count += 1
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames")

            try:
                # Apply YOLO detection to webcam frame
                processed_frame = video_detection_single_frame(frame)
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)

                if not ref or buffer is None:
                    continue

                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam frame: {str(e)}")
                continue

    except Exception as e:
        print(f"Error in api_generate_frames_webcam_raw: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            print("Stable webcam released")




def api_generate_frames_webcam_manufacturing():
    """Generate frames from webcam with Manufacturing PPE detection."""
    global webcam_cap
    max_retries = 15
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam connection successful, starting frame generation (manufacturing)...")
            break
        else:
            print(f"Error: Could not open webcam (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam after retries (manufacturing).")
        return

    try:
        print("Attempting to connect to webcam (manufacturing)...")
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam (manufacturing)")
            return

        print("Webcam connection successful, starting stable frame generation (manufacturing)...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0

        # Load YOLO model once for efficiency
        model = YOLO("YOLO-Weights/bestest.pt")

        while True:
            webcam_cap.grab()
            success, frame = webcam_cap.retrieve()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")

                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True

                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream (manufacturing)")
                    break

                if not success:
                    continue

            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]

                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue

            frame_count += 1
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames (manufacturing)")

            try:
                # Apply Manufacturing PPE detection to webcam frame
                processed_frame = detect_manufacturing_ppe(frame, model)
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)

                if not ref or buffer is None:
                    continue

                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam frame (manufacturing): {str(e)}")
                continue

    except Exception as e:
        print(f"Error in api_generate_frames_webcam_manufacturing: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            print("Stable webcam released (manufacturing)")


from YOLO_Video import detect_construction_ppe

def api_generate_frames_webcam_construction():
    """Generate frames from webcam with Construction PPE detection."""
    global webcam_cap
    max_retries = 15
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam connection successful, starting frame generation (construction)...")
            break
        else:
            print(f"Error: Could not open webcam (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam after retries (construction).")
        return

    try:
        print("Attempting to connect to webcam (construction)...")
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam (construction)")
            return

        print("Webcam connection successful, starting stable frame generation (construction)...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0

        # Load YOLO model once for efficiency
        model = YOLO("YOLO-Weights/bestest.pt")

        while True:
            webcam_cap.grab()
            success, frame = webcam_cap.retrieve()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")

                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True

                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream (construction)")
                    break

                if not success:
                    continue

            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]

                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue

            frame_count += 1
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames (construction)")

            try:
                # Apply Construction PPE detection to webcam frame
                processed_frame = detect_construction_ppe(frame, model)
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)

                if not ref or buffer is None:
                    continue

                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam frame (construction): {str(e)}")
                continue

    except Exception as e:
        print(f"Error in api_generate_frames_webcam_construction: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            print("Stable webcam released (construction)")

# Global variable to hold the webcam capture object
webcam_cap = None

@app.route('/api/release_webcam', methods=['POST'])
def release_webcam():
    global webcam_cap
    print("[DEBUG] /api/release_webcam endpoint called")
    try:
        if webcam_cap is not None:
            webcam_cap.release()
            webcam_cap = None
            print("[DEBUG] Webcam released by API call")
            return jsonify({"status": "released"}), 200
        else:
            print("[DEBUG] No webcam to release")
            return jsonify({"status": "no webcam to release"}), 200
    except Exception as e:
        print(f"[DEBUG] Error releasing webcam: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/webcam_raw')
def webcam_raw():
    """Route to display webcam feed without YOLO detection."""
    print("[DEBUG] /api/webcam_raw endpoint called")
    try:
        return Response(generate_frames_webcam_raw(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_raw route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam_yolo')
def webcam_yolo():
    """Route to display webcam feed with YOLO detection."""
    print("[DEBUG] /api/webcam_yolo endpoint called")
    try:
        return Response(api_generate_frames_webcam_yolo(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_yolo route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam_manufacturing')
def webcam_manufacturing():
    """Route to display webcam feed with Manufacturing PPE detection."""
    print("[DEBUG] /api/webcam_manufacturing endpoint called")
    try:
        return Response(api_generate_frames_webcam_manufacturing(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_manufacturing route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam_construction')
def webcam_construction():
    """Route to display webcam feed with Construction PPE detection."""
    print("[DEBUG] /api/webcam_construction endpoint called")
    try:
        return Response(api_generate_frames_webcam_construction(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_construction route: {str(e)}")
        return jsonify({"error": str(e)}), 500


from YOLO_Video import detect_healthcare_ppe

def api_generate_frames_webcam_healthcare():
    """Generate frames from webcam with Healthcare PPE detection."""
    global webcam_cap
    max_retries = 15
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam connection successful, starting frame generation (healthcare)...")
            break
        else:
            print(f"Error: Could not open webcam (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam after retries (healthcare).")
        return

    try:
        print("Attempting to connect to webcam (healthcare)...")
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam (healthcare)")
            return

        print("Webcam connection successful, starting stable frame generation (healthcare)...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0

        # Load YOLO model once for efficiency
        model = YOLO("YOLO-Weights/bestest.pt")

        while True:
            webcam_cap.grab()
            success, frame = webcam_cap.retrieve()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")

                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True

                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream (healthcare)")
                    break

                if not success:
                    continue

            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]

                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue

            frame_count += 1
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames (healthcare)")

            try:
                # Apply Healthcare PPE detection to webcam frame
                processed_frame = detect_healthcare_ppe(frame, model)
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)

                if not ref or buffer is None:
                    continue

                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam frame (healthcare): {str(e)}")
                continue

    except Exception as e:
        print(f"Error in api_generate_frames_webcam_healthcare: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            print("Stable webcam released (healthcare)")

@app.route('/api/webcam_healthcare')
def webcam_healthcare():
    """Route to display webcam feed with Healthcare PPE detection."""
    print("[DEBUG] /api/webcam_healthcare endpoint called")
    try:
        return Response(api_generate_frames_webcam_healthcare(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_healthcare route: {str(e)}")
        return jsonify({"error": str(e)}), 500

from YOLO_Video import detect_oilgas_ppe

def api_generate_frames_webcam_oilgas():
    """Generate frames from webcam with Oil & Gas PPE detection."""
    global webcam_cap
    max_retries = 15
    retry_delay = 1  # seconds

    # Try to open the webcam with retries
    for attempt in range(max_retries):
        webcam_cap = cv2.VideoCapture(0)
        if webcam_cap.isOpened():
            print("Webcam connection successful, starting frame generation (oilgas)...")
            break
        else:
            print(f"Error: Could not open webcam (attempt {attempt+1}/{max_retries})")
            webcam_cap.release()
            time.sleep(retry_delay)
    else:
        print("Failed to open webcam after retries (oilgas).")
        return

    try:
        print("Attempting to connect to webcam (oilgas)...")
        # Set properties
        webcam_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        webcam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        webcam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        webcam_cap.set(cv2.CAP_PROP_FPS, 15)  # Moderate FPS for stability

        if not webcam_cap.isOpened():
            print("Error: Could not open webcam (oilgas)")
            return

        print("Webcam connection successful, starting stable frame generation (oilgas)...")
        frame_count = 0
        consecutive_failures = 0
        last_valid_frame = None
        frame_skip_counter = 0

        # Load YOLO model once for efficiency
        model = YOLO("YOLO-Weights/bestest.pt")

        while True:
            webcam_cap.grab()
            success, frame = webcam_cap.retrieve()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"Failed to read webcam frame {frame_count}, consecutive failures: {consecutive_failures}")

                if last_valid_frame is not None and consecutive_failures < 5:
                    frame = last_valid_frame.copy()
                    success = True

                if consecutive_failures >= 10:
                    print("Too many webcam failures, stopping stream (oilgas)")
                    break

                if not success:
                    continue

            if frame is not None and frame.size > 0:
                frame_mean = frame.mean()
                h, w = frame.shape[:2]

                if frame_mean > 5 and h > 100 and w > 100:
                    last_valid_frame = frame.copy()
                    consecutive_failures = 0
                else:
                    if last_valid_frame is not None:
                        frame = last_valid_frame.copy()
                    else:
                        continue
            else:
                continue

            frame_count += 1
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            if frame_count % 50 == 0:
                print(f"Processed {frame_count} stable webcam frames (oilgas)")

            try:
                # Apply Oil & Gas PPE detection to webcam frame
                processed_frame = detect_oilgas_ppe(frame, model)
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                ref, buffer = cv2.imencode('.jpg', processed_frame, encode_params)

                if not ref or buffer is None:
                    continue

                frame_bytes = buffer.tobytes()
                if len(frame_bytes) > 100:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing webcam frame (oilgas): {str(e)}")
                continue

    except Exception as e:
        print(f"Error in api_generate_frames_webcam_oilgas: {str(e)}")
    finally:
        if webcam_cap is not None:
            webcam_cap.release()
            print("Stable webcam released (oilgas)")

@app.route('/api/webcam_oilgas')
def webcam_oilgas():
    """Route to display webcam feed with Oil & Gas PPE detection."""
    print("[DEBUG] /api/webcam_oilgas endpoint called")
    try:
        return Response(api_generate_frames_webcam_oilgas(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in webcam_oilgas route: {str(e)}")
        return jsonify({"error": str(e)}), 500    



@app.route('/api/start_violation_recording', methods=['POST'])
def start_violation_recording():
    config.violation_recording_enabled = True
    print("[DEBUG] Violation recording ENABLED")
    return jsonify({"status": "recording started"})

@app.route('/api/stop_violation_recording', methods=['POST'])
def stop_violation_recording():
    config.violation_recording_enabled = False
    violation_recording_enabled = False
    print("[DEBUG] Violation recording DISABLED")
    return jsonify({"status": "recording stopped"})



@app.route('/api/violations/count')
def api_violations_count():
    """
    Returns a count of violations per domain for a given date.
    Example: /api/violations/count?date=2025-07-12
    """
    date_str = request.args.get('date')
    base_dir = "static/violations"
    counts = defaultdict(int)

    # Regex for: violation_<domain>_<YYYYMMDD>_<HHMMSS>_<microseconds>.jpg
    pattern = re.compile(r"violation_(?P<domain>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_\d+\.jpg")

    for domain in os.listdir(base_dir):
        domain_dir = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            match = pattern.match(fname)
            if not match:
                continue
            file_date_str = match.group("date")  # e.g. 20250712
            file_date = datetime.strptime(file_date_str, "%Y%m%d").strftime("%Y-%m-%d")
            if date_str and file_date != date_str:
                continue
            file_domain = match.group("domain")
            counts[file_domain] += 1

    # Return as a list of {domain, count}
    result = [{"domain": domain, "count": count} for domain, count in counts.items()]
    return jsonify(result)

@app.route('/api/violations/timeline')
def api_violations_timeline():
    """
    Returns a timeline (violations per day) for a given date range.
    Example: /api/violations/timeline?from=2025-07-01&to=2025-07-10
    """
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    if not from_date or not to_date:
        return jsonify([])  # or return an error message
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except Exception as e:
        return jsonify([])  # or return an error message
    if from_dt > to_dt:
        return jsonify([])  # or return an error message
    
    base_dir = "static/violations"
    timeline = {}

    # Regex for: violation_<domain>_<YYYYMMDD>_<HHMMSS>_<microseconds>.jpg
    pattern = re.compile(r"violation_(?P<domain>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_\d+\.jpg")

    # Parse date range
    from_dt = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
    to_dt = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None

    for domain in os.listdir(base_dir):
        domain_dir = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            match = pattern.match(fname)
            if not match:
                continue
            file_date_str = match.group("date")  # e.g. 20250712
            file_dt = datetime.strptime(file_date_str, "%Y%m%d")
            file_date = file_dt.strftime("%Y-%m-%d")

            # Filter by date range
            if from_dt and file_dt < from_dt:
                continue
            if to_dt and file_dt > to_dt:
                continue

            timeline[file_date] = timeline.get(file_date, 0) + 1

    # Return sorted list of {date, count}
    result = [{"date": date, "count": timeline[date]} for date in sorted(timeline.keys())]
    return jsonify(result)

@app.route('/api/violations/recent')
def api_violations_recent():
    """
    Returns the most recent violation files, limited by the 'limit' query parameter.
    Example: /api/violations/recent?limit=10
    """
    try:
        limit = int(request.args.get('limit', 10))
    except Exception:
        limit = 10

    base_dir = "static/violations"
    results = []

    # Regex for: violation_<domain>_<YYYYMMDD>_<HHMMSS>_<microseconds>.jpg
    pattern = re.compile(r"violation_(?P<domain>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_\d+\.jpg")

    for domain in os.listdir(base_dir):
        domain_dir = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            match = pattern.match(fname)
            if not match:
                continue
            file_domain = match.group("domain")
            file_date_str = match.group("date")
            file_time_str = match.group("time")
            file_dt = datetime.strptime(file_date_str + file_time_str, "%Y%m%d%H%M%S")
            results.append({
                "filename": f"{domain}/{fname}",
                "domain": file_domain,
                "timestamp": file_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

    # Sort by timestamp descending (most recent first)
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(results[:limit])

@app.route('/api/violations/by_type')
def api_violations_by_type():
    """
    Returns a count of violations by type for a given date,
    considering only those violations that have a saved image file.
    """
    date_str = request.args.get('date')
    DETECTION_RESULTS_FILE = os.getenv("DETECTION_RESULTS_FILE", "detection_results.txt")
    base_dir = "static/violations"
    type_counts = defaultdict(int)

    # Step 1: Build a set of (domain, timestamp) from saved images for the date
    pattern = re.compile(r"violation_(?P<domain>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_(?P<micro>\d+)\.jpg")
    saved_violations = set()
    for domain in os.listdir(base_dir):
        domain_dir = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            match = pattern.match(fname)
            if not match:
                continue
            file_date_str = match.group("date")  # e.g. 20250713
            file_time_str = match.group("time")  # e.g. 214703
            file_micro = match.group("micro")
            file_domain = match.group("domain")
            file_date = f"{file_date_str[:4]}-{file_date_str[4:6]}-{file_date_str[6:]}"
            if file_date != date_str:
                continue
            # Compose a timestamp string for matching (to second precision)
            file_timestamp = f"{file_date} {file_time_str[:2]}:{file_time_str[2:4]}:{file_time_str[4:6]}"
            saved_violations.add((file_domain, file_timestamp))

    # Step 2: Parse DETECTION_RESULTS_FILE and count only those with a matching saved image
    if os.path.exists(DETECTION_RESULTS_FILE):
        with open(DETECTION_RESULTS_FILE, "r") as f:
            for line in f:
                # Example: [2025-07-13 21:47:03] [Manufacturing] NO-hardhat 0.99 (x1, y1, x2, y2)
                m = re.match(r"\[(.*?)\] \[(.*?)\] ([\w\-]+) ([\d\.]+) \((.*?)\)", line)
                if m:
                    time_str, domain, vtype, conf, bbox = m.groups()
                    # Only consider if this detection has a saved image
                    if (domain, time_str) in saved_violations:
                        type_counts[vtype] += 1

    result = [{"type": vtype, "count": count} for vtype, count in type_counts.items()]
    return jsonify(result)

@app.route('/api/violations')
def api_violations():
    """
    Returns a list of violation files filtered by date and time range.
    Example: /api/violations?date=2025-07-12&from=21:00&to=22:00
    """
    date_str = request.args.get('date')
    time_from = request.args.get('from')
    time_to = request.args.get('to')
    # violation_type = request.args.get('type')  # Not used

    base_dir = "static/violations"
    results = []

    # Updated regex for: violation_<domain>_<YYYYMMDD>_<HHMMSS>_<microseconds>.jpg
    pattern = re.compile(r"violation_(?P<domain>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_\d+\.jpg")

    for domain in os.listdir(base_dir):
        domain_dir = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            match = pattern.match(fname)
            if not match:
                continue
            file_domain = match.group("domain")
            file_date_str = match.group("date")      # e.g. 20250712
            file_time_str = match.group("time")      # e.g. 214703

            # Parse datetime
            file_dt = datetime.strptime(file_date_str + file_time_str, "%Y%m%d%H%M%S")
            file_date = file_dt.strftime("%Y-%m-%d")
            file_time = file_dt.strftime("%H:%M")

            # Filter by date
            if date_str and file_date != date_str:
                continue
            # Filter by time range
            if time_from and time_to:
                if not (time_from <= file_time <= time_to):
                    continue

            results.append({
                "filename": f"{domain}/{fname}",
                "domain": file_domain,
                "timestamp": file_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(results)




if __name__ == "__main__":
    # You can specify port and host here
    # Default: http://127.0.0.1:5000
    
    import sys
    
    # Get port from environment variable or command line argument
    port = int(os.environ.get('FLASK_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            host = '0.0.0.0'  # Allow external access when port is specified
            print(f"Starting Flask app on {host}:{port}")
        except ValueError:
            print("Invalid port number. Using default configuration")
    
    print(f"Flask app running on http://{host}:{port}")
    print("Available endpoints:")
    print(f"  - Camera Debug: http://{host}:{port}/camera_debug")
    print(f"  - IP Camera (YOLO): http://{host}:{port}/ipcamera")
    print(f"  - IP Camera (Raw): http://{host}:{port}/ipcamera_raw")
    print(f"  - IP Camera Stable (YOLO): http://{host}:{port}/ipcamera_stable")
    print(f"  - IP Camera Adaptive (YOLO): http://{host}:{port}/ipcamera_adaptive")
    print(f"  - Webcam (YOLO): http://{host}:{port}/webapp")
    
    # Use debug setting from environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, port=port, host=host)

    # Alternative: Directly specify port in code (uncomment one of these):
    
    # For port 8080 (local access only):
    # app.run(debug=False, port=8080, host='127.0.0.1')
    
    # For port 8080 (accessible from other devices on network):
    # app.run(debug=False, port=8080, host='0.0.0.0')
    
    # For port 3000 with custom host:
    # app.run(debug=False, port=3000, host='192.168.1.100')
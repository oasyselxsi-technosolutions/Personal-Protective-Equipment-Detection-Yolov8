#!/usr/bin/env python3
"""
Test script to verify camera functionality
"""

import cv2
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_camera_urls():
    """Test different camera URL formats."""
    camera_urls = [
        "rtsp://admin:Netpro@2025@192.168.8.210:554/stream",
        "rtsp://admin:Netpro@2025@192.168.8.210:554/stream1",
        "rtsp://admin:Netpro@2025@192.168.8.210:554/live",
        "http://admin:Netpro@2025@192.168.8.210:554/stream",
        "http://admin:Netpro@2025@192.168.8.210/video.cgi",
        "http://192.168.8.210/video.cgi?user=admin&pwd=Netpro@2025"
    ]
    
    print("Testing camera URL formats...")
    working_urls = []
    
    for url in camera_urls:
        print(f"\nTesting: {url}")
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✓ SUCCESS: {url} - Frame shape: {frame.shape}")
                    working_urls.append(url)
                else:
                    print(f"✗ FAILED: Connected but no frames from {url}")
            else:
                print(f"✗ FAILED: Could not connect to {url}")
            
            cap.release()
            
        except Exception as e:
            print(f"✗ ERROR: {url} - {str(e)}")
    
    return working_urls

def test_webcam():
    """Test webcam functionality."""
    print("\nTesting webcam...")
    try:
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Webcam working - Frame shape: {frame.shape}")
                return True
            else:
                print("✗ Webcam connected but no frames")
        else:
            print("✗ Could not connect to webcam")
        
        cap.release()
        return False
        
    except Exception as e:
        print(f"✗ Webcam error: {str(e)}")
        return False

def test_yolo_model():
    """Test if YOLO model can be loaded."""
    print("\nTesting YOLO model...")
    try:
        from YOLO_Video import video_detection_single_frame
        import numpy as np
        
        # Create a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Try to process it
        result = video_detection_single_frame(dummy_frame)
        
        if result is not None:
            print("✓ YOLO model loaded and working")
            return True
        else:
            print("✗ YOLO model returned None")
            return False
            
    except Exception as e:
        print(f"✗ YOLO model error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Camera System Test ===")
    
    # Test camera URLs
    working_urls = test_camera_urls()
    
    # Test webcam
    webcam_ok = test_webcam()
    
    # Test YOLO model
    yolo_ok = test_yolo_model()
    
    print("\n=== Test Summary ===")
    print(f"Working IP camera URLs: {len(working_urls)}")
    if working_urls:
        for url in working_urls:
            print(f"  - {url}")
    
    print(f"Webcam: {'✓ Working' if webcam_ok else '✗ Not working'}")
    print(f"YOLO model: {'✓ Working' if yolo_ok else '✗ Not working'}")
    
    if working_urls or webcam_ok:
        print("\n✓ At least one camera source is available")
        if yolo_ok:
            print("✓ Full system ready for operation")
        else:
            print("⚠ Camera available but YOLO detection may not work")
    else:
        print("\n✗ No camera sources available")
        print("Suggestions:")
        print("- Check IP camera network connection")
        print("- Verify camera credentials")
        print("- Connect a webcam to the system")

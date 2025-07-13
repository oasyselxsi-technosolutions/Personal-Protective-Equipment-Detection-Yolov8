# Flask App Logging Setup

This document explains how to run the Flask PPE Detection app with comprehensive logging to help debug issues like the healthcare IP camera feed problem.

## Quick Start

### Option 1: Using the Batch File (Recommended for Windows)
```bash
run_flask_with_logs.bat 5000
```

### Option 2: Direct Python Command with Manual Logging
```bash
python flaskapp.py 5000 > logs\output.log 2>&1
```

### Option 3: Using PowerShell Script
```powershell
.\run_flask_with_logs.ps1 5000
```

## Log Files Created

When you run the app with logging, several log files are created in the `logs/` directory:

1. **`flaskapp.log`** - Main application log with detailed debugging information
2. **`flask_output_YYYYMMDD_HHMMSS.log`** - Console output capture
3. **`runtime.log`** - Runtime script logging (if using Python runner)

## Key Log Categories

The logs use emojis and categories to make them easier to read:

- 🚀 `[STARTUP]` - Application startup and configuration
- 🏥 `[HEALTHCARE]` - Healthcare-specific route debugging  
- 🎯 `[DOMAIN-*]` - Domain-specific route processing
- 🎬 `[FRAME-GEN-*]` - Frame generation and camera processing
- ❌ `[ERROR]` - Error conditions
- ✅ `[SUCCESS]` - Successful operations

## Debugging the Healthcare Feed Issue

### Step 1: Start the App with Logging
```bash
run_flask_with_logs.bat 5000
```

### Step 2: Test the Healthcare Route
```bash
python test_healthcare_route.py
```

### Step 3: Check the Logs
1. Open `logs/flaskapp.log` and search for:
   - `[HEALTHCARE]` - Healthcare-specific logs
   - `[DOMAIN-HEALTHCARE]` - Domain processing for healthcare
   - `[FRAME-GEN-HEALTHCARE]` - Frame generation for healthcare

### Step 4: Check React Console
Open browser dev tools and look for:
- `🎥 [CameraFeed]` - React component logs
- `🏥 [CameraFeed]` - Healthcare-specific frontend logs

## Common Issues and Solutions

### Issue: "Cannot connect to IP camera"
**Look for:** `[DOMAIN-HEALTHCARE]` logs showing camera URL testing
**Solution:** Check camera IP, credentials, and network connectivity

### Issue: "Route returns 500 error"
**Look for:** `❌ [HEALTHCARE]` error logs
**Solution:** Check YOLO model files and dependencies

### Issue: "Frontend shows 'Unable to connect'"
**Look for:** `❌ [CameraFeed] Image load error` in browser console
**Solution:** Verify backend route is responding correctly

### Issue: "Stream starts but no frames"
**Look for:** `[FRAME-GEN-HEALTHCARE]` logs showing frame processing
**Solution:** Check camera stream format and YOLO processing

## Environment Variables

Make sure these are set correctly (check startup logs):
- `CAMERA_IP` - IP address of your camera
- `CAMERA_USERNAME` - Camera login username  
- `CAMERA_PASSWORD` - Camera login password
- `CAMERA_PORT` - Camera port (usually 554 for RTSP)

## Advanced Debugging

### Enable More Verbose Logging
Set environment variable:
```bash
set FLASK_DEBUG=true
```

### Check Specific Domain Function
The logs will show which detection function is being used:
- `detect_healthcare_ppe` for healthcare domain
- `video_detection_single_frame` for general domain

### Monitor Camera Connection
Look for these log patterns:
```
🎯 [DOMAIN-HEALTHCARE] Testing camera URL 1/8: rtsp://...
✅ [DOMAIN-HEALTHCARE] Successfully connected to: rtsp://...
🎬 [FRAME-GEN-HEALTHCARE] Starting frame generation
```

## Log File Rotation

The main `flaskapp.log` automatically rotates when it reaches 10MB, keeping 5 backup files. This prevents the logs from consuming too much disk space.

## Clean Up Logs

To clean up old log files:
```bash
# Delete all log files older than 7 days
forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"
```

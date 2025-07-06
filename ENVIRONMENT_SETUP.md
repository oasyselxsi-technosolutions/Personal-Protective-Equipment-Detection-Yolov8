# Environment Setup Guide

## Overview
This PPE Detection application has been refactored to use environment variables for camera configuration instead of hardcoded credentials. This improves security by keeping sensitive information out of the source code.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` with your camera details:
```env
# Camera Configuration
CAMERA_IP=192.168.8.210
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_camera_password
CAMERA_PORT=554

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True
```

### 3. Run the Application
```bash
python flaskapp.py
```

The application will start on `http://127.0.0.1:5000` with the following endpoints:
- **Camera Debug**: `http://127.0.0.1:5000/camera_debug`
- **IP Camera (YOLO)**: `http://127.0.0.1:5000/ipcamera`
- **IP Camera (Raw)**: `http://127.0.0.1:5000/ipcamera_raw`
- **Webcam (YOLO)**: `http://127.0.0.1:5000/webapp`

## Environment Variables

### Camera Settings
- `CAMERA_IP`: Your IP camera's IP address
- `CAMERA_USERNAME`: Username for camera authentication
- `CAMERA_PASSWORD`: Password for camera authentication
- `CAMERA_PORT`: RTSP port (usually 554)

### Flask Settings
- `FLASK_HOST`: Host address (default: 127.0.0.1)
- `FLASK_PORT`: Port number (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (True/False)

## Security Features

### What's Protected
- Camera IP addresses
- Camera usernames and passwords
- All authentication credentials

### Git Security
- `.env` file is excluded from git via `.gitignore`
- `.env.example` provides a safe template without real credentials
- All sensitive data stays local to your machine

## Camera URL Formats

The application automatically tests multiple camera URL formats:

1. **RTSP Streams**:
   - `rtsp://{username}:{password}@{ip}:{port}/stream`
   - `rtsp://{username}:{password}@{ip}:{port}/stream1`
   - `rtsp://{username}:{password}@{ip}:{port}/live`
   - `rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel=1&subtype=0`

2. **HTTP Streams**:
   - `http://{username}:{password}@{ip}:{port}/stream`
   - `http://{username}:{password}@{ip}/video.cgi`
   - `http://{username}:{password}@{ip}/videostream.cgi`
   - `http://{ip}/video.cgi?user={username}&pwd={password}`

## Troubleshooting

### Environment Issues
1. **Environment file not found**: Ensure `.env` exists and has correct format
2. **Variables not loading**: Check for syntax errors in `.env` file
3. **Default values used**: Verify environment variable names match exactly

### Camera Connection Issues
1. **Test network connectivity**: `ping {your_camera_ip}`
2. **Verify camera web interface**: Open `http://{your_camera_ip}` in browser
3. **Check credentials**: Ensure username/password are correct
4. **Port accessibility**: Verify ports 554 (RTSP) and 80 (HTTP) are open

### Application Issues
1. **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
2. **Permission errors**: Check camera privacy settings on Windows
3. **Performance issues**: YOLO detection requires sufficient CPU/GPU resources

## Development Notes

### File Changes Made
- `flaskapp.py`: Refactored to use environment variables
- `.env`: Created for local configuration (not in git)
- `.env.example`: Template for sharing setup
- `.gitignore`: Updated to exclude sensitive files
- `requirements.txt`: Added `python-dotenv`
- Documentation updated to reflect new setup

### Testing
All endpoints have been tested and confirmed working:
- ✅ Environment variable loading
- ✅ Camera URL generation
- ✅ Flask application startup
- ✅ All routes accessible

## Best Practices

1. **Never commit `.env`**: Always keep credentials local
2. **Update `.env.example`**: When adding new variables, update the example
3. **Use strong passwords**: Ensure camera credentials are secure
4. **Regular updates**: Keep dependencies updated for security
5. **Network security**: Secure your camera network appropriately

## Support

If you encounter issues:
1. Check this guide for common solutions
2. Review `CAMERA_FIXES_README.md` for camera-specific issues
3. Verify environment setup matches `.env.example`
4. Test camera connectivity independently

## Migration from Previous Versions

If upgrading from a version with hardcoded credentials:
1. Copy `.env.example` to `.env`
2. Fill in your actual camera credentials
3. Install `python-dotenv`: `pip install python-dotenv`
4. Restart the application

The application will automatically use the new environment-based configuration.

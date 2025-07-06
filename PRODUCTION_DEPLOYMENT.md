# Production Deployment Guide

## Running Flask App in Production Mode

This guide covers different ways to run your PPE Detection Flask application in production mode without debug features.

## Quick Start - Production Mode

### Option 1: Basic Production Mode (Flask Built-in Server)
```cmd
# Windows
run_flask_production.bat

# Or manually:
set FLASK_DEBUG=False
set FLASK_ENV=production
python flaskapp.py
```

### Option 2: Waitress Server (Recommended for Windows)
```cmd
# Windows - Automated setup and run
run_production_waitress.bat

# Or manually:
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

### Option 3: Gunicorn Server (Linux/Unix)
```bash
# Linux/Unix
chmod +x run_production_gunicorn.sh
./run_production_gunicorn.sh

# Or manually:
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
```

## Environment Configuration

### Production .env Settings
```properties
# Camera Configuration
CAMERA_IP=192.168.8.210
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your-secure-password
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

**⚠️ Important Security Notes:**
- Change `FLASK_SECRET_KEY` to a secure random string
- Use strong camera passwords
- Never commit `.env` file to version control

## Production Server Comparison

| Server | Platform | Performance | Ease of Setup | Recommended For |
|--------|----------|-------------|---------------|-----------------|
| **Flask Built-in** | All | Low | Very Easy | Development/Testing |
| **Waitress** | Windows/All | Medium | Easy | Windows Production |
| **Gunicorn** | Linux/Unix | High | Medium | Linux Production |
| **uWSGI** | Linux/Unix | High | Hard | Enterprise Linux |

## Server Configuration Details

### Waitress (Windows Production)
```cmd
# Basic usage
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app

# With more workers and threading
waitress-serve --host=0.0.0.0 --port=5000 --threads=8 --connection-limit=1000 wsgi:app

# Background service
waitress-serve --host=0.0.0.0 --port=5000 --daemon wsgi:app
```

### Gunicorn (Linux Production)
```bash
# Basic usage
gunicorn --bind 0.0.0.0:5000 wsgi:app

# Production configuration
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --worker-class sync \
         --timeout 120 \
         --keep-alive 2 \
         --max-requests 1000 \
         --preload \
         wsgi:app

# Background daemon
gunicorn --bind 0.0.0.0:5000 --workers 4 --daemon --pid /tmp/gunicorn.pid wsgi:app
```

## Performance Optimization

### For High Traffic
1. **Increase Workers**: More CPU cores = more workers
   ```bash
   # Gunicorn: workers = (2 x CPU cores) + 1
   gunicorn --workers 8 --bind 0.0.0.0:5000 wsgi:app
   
   # Waitress: increase threads
   waitress-serve --threads=16 --host=0.0.0.0 --port=5000 wsgi:app
   ```

2. **Optimize Camera Settings**:
   ```properties
   CAMERA_WIDTH=320     # Lower resolution for faster processing
   CAMERA_HEIGHT=240
   CAMERA_BUFFER_SIZE=1 # Minimal buffering
   ```

3. **Use Adaptive Endpoints**: For high-resolution cameras
   ```
   /ipcamera_adaptive
   /ipcamera_adaptive_raw
   ```

## Production Checklist

### Before Deployment
- [ ] Set `FLASK_DEBUG=False` in `.env`
- [ ] Generate secure `FLASK_SECRET_KEY`
- [ ] Test camera connectivity with `test_camera.py`
- [ ] Verify all endpoints work via `/camera_debug`
- [ ] Configure Windows Firewall rules
- [ ] Test network access from other machines

### Security Hardening
- [ ] Use HTTPS in production (add SSL certificates)
- [ ] Implement authentication for camera feeds
- [ ] Restrict firewall rules to specific IP ranges
- [ ] Regular password changes for camera access
- [ ] Monitor access logs

### Performance Monitoring
- [ ] Monitor CPU usage during YOLO processing
- [ ] Check memory usage with multiple camera streams
- [ ] Test concurrent user access
- [ ] Monitor network bandwidth usage

## Troubleshooting Production Issues

### Flask App Won't Start
```cmd
# Check environment variables
echo %FLASK_DEBUG%
echo %FLASK_HOST%
echo %FLASK_PORT%

# Test basic Python execution
python -c "import flaskapp; print('Import successful')"
```

### Network Access Issues
```cmd
# Check if port is listening
netstat -an | findstr :5000

# Test local access first
curl http://127.0.0.1:5000/test_camera

# Test network access
curl http://192.168.8.219:5000/test_camera
```

### Camera Connection Issues
```cmd
# Test camera directly
python test_camera.py

# Check camera network connectivity
ping 192.168.8.210
```

### Performance Issues
1. **High CPU Usage**: Reduce camera resolution or frame rate
2. **Memory Leaks**: Use stable endpoints (`/ipcamera_stable`)
3. **Slow Streaming**: Use raw endpoints (`/ipcamera_raw`)
4. **Connection Drops**: Use adaptive endpoints (`/ipcamera_adaptive`)

## Production URLs

Once running in production, share these URLs with users:

```
🌐 Main Application: http://192.168.8.219:5000
🔧 Debug Interface: http://192.168.8.219:5000/camera_debug
📹 YOLO Detection: http://192.168.8.219:5000/ipcamera
📱 Raw Stream: http://192.168.8.219:5000/ipcamera_raw
🔧 Stable Stream: http://192.168.8.219:5000/ipcamera_stable
⚡ Adaptive Stream: http://192.168.8.219:5000/ipcamera_adaptive
```

## Service Installation (Optional)

For automatic startup on Windows, you can install the Flask app as a Windows service:

1. Install `python-windows-service` package
2. Create service wrapper script
3. Register with Windows Service Manager

This ensures your PPE detection system starts automatically when the server boots.

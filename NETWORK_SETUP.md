# Network Setup Guide

## Making Flask Application Available Over Network

Your Flask application is now configured to be accessible from other machines on the network.

## Configuration Changes Made

### 1. Updated .env Configuration
```properties
FLASK_HOST=0.0.0.0  # Changed from 127.0.0.1 to allow network access
FLASK_PORT=5000     # Port for the application
```

### 2. Network Access Information

**Your Machine's IP Addresses:**
- Primary Network: `192.168.8.219`
- Secondary: `172.26.32.1`

**Application URLs for Network Access:**
- Main Application: `http://192.168.8.219:5000`
- Camera Debug Page: `http://192.168.8.219:5000/camera_debug`
- IP Camera Stream (YOLO): `http://192.168.8.219:5000/ipcamera`
- IP Camera Stream (Raw): `http://192.168.8.219:5000/ipcamera_raw`
- Webcam Stream: `http://192.168.8.219:5000/webapp`
- Stable Endpoints: `http://192.168.8.219:5000/ipcamera_stable`
- Adaptive Endpoints: `http://192.168.8.219:5000/ipcamera_adaptive`

## Firewall Configuration

### Windows Firewall Rule Required
To allow other machines to connect, you need to add a Windows Firewall rule. Run this command as Administrator:

```cmd
netsh advfirewall firewall add rule name="Python Flask App" dir=in action=allow protocol=TCP localport=5000
```

### Alternative: Windows Firewall GUI Method
1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → "TCP" → Specific local ports: `5000`
4. Allow the connection
5. Apply to all profiles (Domain, Private, Public)
6. Name: "Python Flask App"

## Testing Network Access

### From Other Machines on the Same Network:
1. **Open web browser** on another machine
2. **Navigate to**: `http://192.168.8.219:5000/camera_debug`
3. **Test camera feeds** using the debug interface

### Command Line Testing:
```bash
# Test connectivity from another machine
curl http://192.168.8.219:5000/test_camera

# Or use ping to test basic connectivity
ping 192.168.8.219
```

## Mobile Device Access

Your application is now accessible from mobile devices on the same network:
- **iPhone/Android**: Open browser → `http://192.168.8.219:5000`
- **Camera streams work** on mobile browsers
- **Touch-friendly** debug interface available

## Port Configuration

### Using Different Ports:
If port 5000 is blocked or in use, you can change it:

1. **Update .env file:**
   ```properties
   FLASK_PORT=8080  # or any available port
   ```

2. **Update firewall rule:**
   ```cmd
   netsh advfirewall firewall add rule name="Python Flask App 8080" dir=in action=allow protocol=TCP localport=8080
   ```

3. **Access URLs become:**
   ```
   http://192.168.8.219:8080/camera_debug
   ```

## Security Considerations

### For Production Use:
1. **Use HTTPS** instead of HTTP
2. **Add authentication** to protect camera feeds
3. **Restrict firewall rules** to specific IP ranges
4. **Use a production WSGI server** (not Flask development server)

### Current Development Setup:
- ✅ **Local network access enabled**
- ✅ **All endpoints accessible**
- ⚠️ **No authentication** (development only)
- ⚠️ **HTTP only** (not encrypted)

## Troubleshooting Network Access

### If Other Machines Can't Connect:

1. **Check Windows Firewall:**
   ```cmd
   netsh advfirewall firewall show rule name="Python Flask App"
   ```

2. **Verify Flask is listening on all interfaces:**
   ```cmd
   netstat -an | findstr :5000
   ```
   Should show: `0.0.0.0:5000`

3. **Test from local machine first:**
   ```
   http://192.168.8.219:5000/camera_debug
   ```

4. **Check network connectivity:**
   ```cmd
   ping 192.168.8.219  # from other machine
   ```

5. **Verify same network segment:**
   - Ensure all machines are on same WiFi/network
   - Check IP ranges match (192.168.8.x)

### Common Issues:

| Issue | Solution |
|-------|----------|
| Connection refused | Add firewall rule |
| Page not loading | Check Flask is running |
| Can't see camera | Verify camera IP is accessible from server |
| Slow streaming | Reduce resolution or use raw endpoints |

## Network Performance Tips

### For Better Streaming Performance:
1. **Use wired connection** for the Flask server
2. **Use stable endpoints** (`/ipcamera_stable`) for reliability
3. **Use raw endpoints** (`/ipcamera_raw`) for faster streaming
4. **Limit concurrent connections** to camera feeds

### Camera Stream URLs for Direct Access:
- **YOLO Detection**: `http://192.168.8.219:5000/ipcamera`
- **Raw Stream**: `http://192.168.8.219:5000/ipcamera_raw`
- **Stable Stream**: `http://192.168.8.219:5000/ipcamera_stable`
- **Adaptive Stream**: `http://192.168.8.219:5000/ipcamera_adaptive`

## Quick Start for Network Users

Share these URLs with other users on your network:

```
🌐 Main Application: http://192.168.8.219:5000
🔧 Debug Interface: http://192.168.8.219:5000/camera_debug
📹 Camera Stream: http://192.168.8.219:5000/ipcamera
📱 Mobile Friendly: Works on phones/tablets
```

The application is now fully network-enabled and ready for multi-user access!

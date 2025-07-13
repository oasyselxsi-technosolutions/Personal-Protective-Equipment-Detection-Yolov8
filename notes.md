# Clean build

npm run clean
npm run build
npm start

---

4. npm Clean (Optional)
   If you suspect a corrupted node_modules or build cache:

rm -rf node_modules
npm install
npm run build

---

## To display the API routes in flask application

`flask routes`

flask routes
Endpoint                   Methods    Rule

-------------------------  ---------  ------------------------------

api_violations             GET        /api/violations
camera_debug               GET        /camera_debug
dashboard                  GET        /api/dashboard
front                      GET, POST  /FrontPage
home                       GET, POST  /home
home                       GET, POST  /
ipcamera                   GET        /ipcamera
ipcamera_adaptive          GET        /ipcamera_adaptive
ipcamera_adaptive_raw      GET        /ipcamera_adaptive_raw
ipcamera_raw               GET        /ipcamera_raw
ipcamera_stable            GET        /ipcamera_stable
ipcamera_stable_raw        GET        /ipcamera_stable_raw
release_webcam             POST       /api/release_webcam
start_violation_recording  POST       /api/start_violation_recording
static                     GET        /static/<path:filename>
stop_violation_recording   POST       /api/stop_violation_recording
test_camera                GET        /test_camera
video                      GET        /video
webapp                     GET        /webapp
webapp_stable              GET        /webapp_stable
webcam                     GET, POST  /webcam
webcam_construction        GET        /api/webcam_construction
webcam_feed                GET        /webcam_feed
webcam_healthcare          GET        /api/webcam_healthcare
webcam_manufacturing       GET        /api/webcam_manufacturing
webcam_oilgas              GET        /api/webcam_oilgas
webcam_raw                 GET        /api/webcam_raw
webcam_yolo                GET        /api/webcam_yolo

---

## Segmentation fault error

webcam (raw) connection successful, starting frame generation...
0: 608x800 1 NO-Hardhat, 1 NO-Safety Vest, 1 Person, 26.6ms
Speed: 0.7ms preprocess, 26.6ms inference, 1.9ms postprocess per image at shape (1, 3, 800, 800)
[DEBUG] violation_detected=True, violation_recording_enabled=False
Error in api_generate_frames_webcam_construction: OpenCV(4.7.0) /io/opencv/modules/core/src/matrix_c.cpp:190: error: (-5:Bad argument) Unknown array type in function 'cvarrToMat'

Stable webcam released (construction)
Segmentation fault (core dumped)

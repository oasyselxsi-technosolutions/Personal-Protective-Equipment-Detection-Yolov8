const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

export type CameraFeedConfig = {
  id: string;
  name: string;
  location: string;
  type: string;
  url: string;
};

export const cameraFeeds: CameraFeedConfig[] = [
  {
    id: "webcam_raw",
    name: "Webcam - Raw Feed",
    location: "Local Computer",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_raw`
  },
  {
    id: "webcam_yolo",
    name: "Webcam - YOLO Detection",
    location: "Local Computer", 
    type: "webcam",
    url: `${API_BASE_URL}/webcam_yolo`
  },
  {
    id: "webcam_healthcare",
    name: "Webcam - Healthcare PPE",
    location: "Healthcare Facility",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_healthcare`
  },
  {
    id: "webcam_manufacturing",
    name: "Webcam - Manufacturing PPE",
    location: "Manufacturing Floor",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_manufacturing`
  },
  {
    id: "webcam_construction",
    name: "Webcam - Construction PPE",
    location: "Construction Site",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_construction`
  },
  {
    id: "webcam_oilgas",
    name: "Webcam - Oil & Gas PPE",
    location: "Oil & Gas Facility",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_oilgas`
  },
  // IP Camera feeds (disabled until physical camera is available)
  // {
  //   id: "gate2",
  //   name: "Demo IP Camera - Stable Raw",
  //   location: "Room",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable_raw/general"
  // },
  // {
  //   id: "gate2_yolo",
  //   name: "Demo IP Camera - Stable YOLO",
  //   location: "Room",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable/general"
  // },
  // {
  //   id: "ipcamera_manufacturing",
  //   name: "IP Camera - Manufacturing PPE",
  //   location: "Manufacturing Floor",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable/manufacturing"
  // },
  // {
  //   id: "ipcamera_construction",
  //   name: "IP Camera - Construction PPE",
  //   location: "Construction Site",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable/construction"
  // },
  // {
  //   id: "ipcamera_healthcare",
  //   name: "IP Camera - Healthcare PPE",
  //   location: "Healthcare Facility",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable/healthcare"
  // },
  // {
  //   id: "ipcamera_oilgas",
  //   name: "IP Camera - Oil & Gas PPE",
  //   location: "Oil & Gas Facility",
  //   type: "ipcamera",
  //   url: "http://localhost:5000/ipcamera_stable/oilgas"
  // },
];
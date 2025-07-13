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
    id: "gate1",
    name: "Webcam at- RAW",
    location: "Site Gate",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_raw`
  },
  {
    id: "gate2",
    name: "Gate #2",
    location: "Room",
    type: "ipcamera",
    url: `${API_BASE_URL}/webcam_yolo`
  },
  {
    id: "webcam_yolo_manufacturing",
    name: "Webcam Manufacturing",
    location: "Manufacturing Floor",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_manufacturing`
  },
  {
    id: "webcam_yolo_construction",
    name: "Webcam Construction",
    location: "Construction Floor",
    type: "webcam",
    url: `${API_BASE_URL}/webcam_construction`
  }
];
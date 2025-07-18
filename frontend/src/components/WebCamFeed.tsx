import React, { useState, useEffect } from 'react';

// Use environment variable for API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

// Helper to get the static base (for images)
function getStaticBaseUrl() {
  // Remove trailing /api if present
  return API_BASE_URL.replace(/\/api\/?$/, "");
}

const CAMERA_OPTIONS = [
  { label: "Webcam (Raw)", value: `${API_BASE_URL}/webcam_raw` },
  { label: "Webcam (YOLO)", value: `${API_BASE_URL}/webcam_yolo` },
  { label: "Webcam (Manufacturing PPE)", value: `${API_BASE_URL}/webcam_manufacturing` },
  { label: "Webcam (Construction PPE)", value: `${API_BASE_URL}/webcam_construction` },
  { label: "Webcam (Healthcare PPE)", value: `${API_BASE_URL}/webcam_healthcare` },
  { label: "Webcam (Oil & Gas PPE)", value: `${API_BASE_URL}/webcam_oilgas` }
];

// Helper to format time as "08:00 AM"
function formatTime(t: string) {
  if (!t) return "--:--";
  const [h, m] = t.split(":");
  let hour = parseInt(h, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  hour = hour % 12 || 12;
  return `${hour.toString().padStart(2, "0")}:${m} ${ampm}`;
}

// Helper to generate time options in "HH:MM" 24-hour format
function generateTimeOptions(stepMinutes = 30) {
  const options = [];
  for (let h = 0; h < 24; h++) {
    for (let m = 0; m < 60; m += stepMinutes) {
      const hour = h.toString().padStart(2, "0");
      const min = m.toString().padStart(2, "0");
      options.push(`${hour}:${min}`);
    }
  }
  return options;
}

const timeOptions = generateTimeOptions(30); // every 30 minutes

// Helper to get today's date in YYYY-MM-DD format
function getToday() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

const WebCamFeed: React.FC = () => {
  const [selectedFeed, setSelectedFeed] = useState(CAMERA_OPTIONS[0].value);
  const [imgKey, setImgKey] = useState(Date.now());
  const [showFeed, setShowFeed] = useState(true);
  const [recording, setRecording] = useState(false);
  const [date, setDate] = useState('');
  const [timeRange, setTimeRange] = useState({ from: '07:00', to: '08:00' });
  const [violationFiles, setViolationFiles] = useState<any[]>([]);
  const [selectedViolationFile, setSelectedViolationFile] = useState<any>(null);

  // Set today's date and default time range on mount
  useEffect(() => {
    setDate(getToday());
    setTimeRange({ from: '07:00', to: '08:00' });
  }, []);

  // Fetch violation files when filters change (without violation type)
  useEffect(() => {
    if (!date || !timeRange.from || !timeRange.to) {
      setViolationFiles([]);
      setSelectedViolationFile(null);
      return;
    }
    const params = new URLSearchParams({
      date,
      from: timeRange.from,
      to: timeRange.to
    });
    fetch(`${API_BASE_URL}/violations?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setViolationFiles(data || []);
        setSelectedViolationFile(null);
      })
      .catch(() => {
        setViolationFiles([]);
        setSelectedViolationFile(null);
      });
  }, [date, timeRange]);

  const handleRadioChange = async (value: string) => {
    setShowFeed(false);
    try {
      await fetch(`${API_BASE_URL}/release_webcam`, { method: 'POST' });
    } catch {}
    setTimeout(() => {
      setSelectedFeed(value);
      setImgKey(Date.now());
      setShowFeed(true);
    }, 500);
  };

  const handleRecordingToggle = async () => {
    const action = recording ? 'stop' : 'start';
    const endpoint = recording
      ? `${API_BASE_URL}/stop_violation_recording`
      : `${API_BASE_URL}/start_violation_recording`;
    
    console.log(`🎬 [WebCamFeed] Attempting to ${action} violation recording`);
    console.log(`🎬 [WebCamFeed] Endpoint: ${endpoint}`);
    
    try {
      const response = await fetch(endpoint, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`🎬 [WebCamFeed] Response status: ${response.status}`);
      
      if (response.ok) {
        const result = await response.json().catch(() => ({}));
        console.log(`✅ [WebCamFeed] Successfully ${action}ed violation recording`, result);
        setRecording(!recording);
        
        // Show success message
        const message = recording ? 'Violation recording stopped' : 'Violation recording started';
        console.log(`🎬 [WebCamFeed] ${message}`);
      } else {
        const errorText = await response.text().catch(() => 'Unknown error');
        console.error(`❌ [WebCamFeed] Failed to ${action} recording: ${response.status} - ${errorText}`);
        alert(`Failed to ${action} violation recording: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error(`❌ [WebCamFeed] Network error during ${action} recording:`, error);
      alert(`Failed to ${action} violation recording. Please check if the backend is running.`);
    }
  };

  const handleImageLoad = () => {};
  const handleImageError = () => {
    alert('Could not open webcam. Make sure no other stream is using it.');
  };

  const imgSrc = `${selectedFeed}?t=${imgKey}`;

  // Compose the time range string for display
  const timeRangeDisplay =
    timeRange.from && timeRange.to
      ? `${formatTime(timeRange.from)} - ${formatTime(timeRange.to)}`
      : "Select time range";

  return (
    <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-start' }}>
      {/* Left: Camera Feed and Controls */}
      <div style={{ minWidth: 700, marginRight: 40 }}>
        {/* Header Row */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "1.5em"
        }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <h2 style={{ margin: 0, marginRight: "1.5em" }}>Camera Feed</h2>
            <button
              onClick={handleRecordingToggle}
              style={{
                padding: "0.5em 1.5em",
                borderRadius: "8px",
                background: recording ? "#d32f2f" : "#1976d2",
                color: "#fff",
                border: "none",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              {recording ? "Stop Recording Violations" : "Start Recording Violations"}
            </button>
          </div>
          {/* Date/Time Range Selector */}
          <div style={{ display: "flex", alignItems: "center" }}>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              style={{ marginRight: "0.5em" }}
            />
            <select
              value={timeRange.from}
              onChange={e => setTimeRange({ ...timeRange, from: e.target.value })}
              style={{ marginRight: "0.5em" }}
            >
              {timeOptions.map(t => (
                <option key={t} value={t}>{formatTime(t)}</option>
              ))}
            </select>
            <span style={{ margin: "0 0.5em" }}>to</span>
            <select
              value={timeRange.to}
              onChange={e => setTimeRange({ ...timeRange, to: e.target.value })}
              style={{ marginRight: "1em" }}
            >
              {timeOptions.map(t => (
                <option key={t} value={t}>{formatTime(t)}</option>
              ))}
            </select>
            <span style={{ fontWeight: 500, color: "#555", marginRight: "1em" }}>
              {timeRangeDisplay}
            </span>
          </div>
        </div>

        {/* Camera Options */}
        <div style={{ marginBottom: 24 }}>
          {CAMERA_OPTIONS.map(option => (
            <label key={option.value} style={{ marginRight: "1em" }}>
              <input
                type="radio"
                name="cameraFeed"
                value={option.value}
                checked={selectedFeed === option.value}
                onChange={() => handleRadioChange(option.value)}
              />
              {option.label}
            </label>
          ))}
        </div>

        {/* Camera Feed */}
        <div
          style={{
            background: "#fff",
            borderRadius: "18px",
            boxShadow: "0 2px 12px rgba(0,0,0,0.07)",
            padding: "1.5em",
            width: "fit-content",
            display: "inline-block"
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: "1em", color: "#222" }}>
            {CAMERA_OPTIONS.find(opt => opt.value === selectedFeed)?.label || "Feed"}
          </div>
          {showFeed && (
            <img
              key={imgKey}
              src={imgSrc}
              alt="Camera Feed"
              style={{
                width: '640px',
                border: '1px solid #eee',
                borderRadius: '14px',
                boxShadow: '0 1px 6px rgba(0,0,0,0.06)'
              }}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          )}
        </div>
      </div>

      {/* Right: Violation Files List and Selected Image */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Violation Files Scrollable List */}
        <div style={{
          width: 340,
          height: 500,
          overflowY: 'auto',
          border: '1px solid #eee',
          borderRadius: 8,
          marginBottom: 24,
          background: '#fafbfc'
        }}>
          {violationFiles.length === 0 && (
            <div style={{ padding: 24, color: '#aaa', textAlign: 'center' }}>
              No violation files found for the selected filters.
            </div>
          )}
          {violationFiles.map(file => (
            <div
              key={file.filename}
              style={{
                padding: 12,
                cursor: 'pointer',
                background: selectedViolationFile && selectedViolationFile.filename === file.filename ? '#e6f0fa' : 'transparent',
                borderBottom: '1px solid #f0f0f0'
              }}
              onClick={() => setSelectedViolationFile(file)}
            >
              <div><b>{file.domain || file.type || "Violation"}</b></div>
              <div style={{ fontSize: 12, color: '#888' }}>{file.timestamp}</div>
              <div style={{ fontSize: 12, color: '#888' }}>{file.filename}</div>
            </div>
          ))}
        </div>
        {/* Selected Violation File Display */}
        <div>
          {selectedViolationFile && (
            <img
              src={`${getStaticBaseUrl()}/static/violations/${selectedViolationFile.filename}`}
              alt="Violation"
              style={{
                maxWidth: 320,
                maxHeight: 320,
                borderRadius: 8,
                border: '1px solid #eee'
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default WebCamFeed;
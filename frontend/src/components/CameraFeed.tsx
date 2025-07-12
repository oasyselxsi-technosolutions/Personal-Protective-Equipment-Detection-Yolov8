import React, { useState, useEffect } from 'react';

const host = "localhost";
const port = 5000;

const CAMERA_OPTIONS = [
  { label: "Webcam (Raw)", value: `http://${host}:${port}/api/webcam_raw` },
  { label: "Webcam (YOLO)", value: `http://${host}:${port}/api/webcam_yolo` },
  { label: "Webcam (Manufacturing PPE)", value: `http://${host}:${port}/api/webcam_manufacturing` },
  { label: "Webcam (Construction PPE)", value: `http://${host}:${port}/api/webcam_construction` },
  { label: "Webcam (Healthcare PPE)", value: `http://${host}:${port}/api/webcam_healthcare` },
  { label: "Webcam (Oil & Gas PPE)", value: `http://${host}:${port}/api/webcam_oilgas` }
];

const VIOLATION_TYPES = [
  { label: "NO-Hardhat", value: "NO-Hardhat" },
  { label: "NO-Mask", value: "NO-Mask" },
  { label: "NO-Safety Vest", value: "NO-Safety Vest" }
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

const CameraFeed: React.FC = () => {
  const [selectedFeed, setSelectedFeed] = useState(CAMERA_OPTIONS[0].value);
  const [imgKey, setImgKey] = useState(Date.now());
  const [showFeed, setShowFeed] = useState(true);
  const [recording, setRecording] = useState(false);
  const [date, setDate] = useState('');
  const [timeRange, setTimeRange] = useState({ from: '08:00', to: '09:00' });
  const [violationType, setViolationType] = useState('');
  const [violationFiles, setViolationFiles] = useState<any[]>([]);
  const [selectedViolationFile, setSelectedViolationFile] = useState<any>(null);

  // Fetch violation files when filters change
  useEffect(() => {
    if (!date || !timeRange.from || !timeRange.to || !violationType) {
      setViolationFiles([]);
      setSelectedViolationFile(null);
      return;
    }
    const params = new URLSearchParams({
      date,
      from: timeRange.from,
      to: timeRange.to,
      type: violationType
    });
    fetch(`http://${host}:${port}/api/violations?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setViolationFiles(data || []);
        setSelectedViolationFile(null);
      })
      .catch(() => {
        setViolationFiles([]);
        setSelectedViolationFile(null);
      });
  }, [date, timeRange, violationType]);

  const handleRadioChange = async (value: string) => {
    setShowFeed(false);
    try {
      await fetch(`http://${host}:${port}/api/release_webcam`, { method: 'POST' });
    } catch {}
    setTimeout(() => {
      setSelectedFeed(value);
      setImgKey(Date.now());
      setShowFeed(true);
    }, 500);
  };

  const handleRecordingToggle = async () => {
    const endpoint = recording
      ? `http://${host}:${port}/api/stop_violation_recording`
      : `http://${host}:${port}/api/start_violation_recording`;
    try {
      await fetch(endpoint, { method: 'POST' });
      setRecording(!recording);
    } catch {
      alert('Failed to toggle violation recording');
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
            <select
              value={violationType}
              onChange={e => setViolationType(e.target.value)}
              style={{ marginRight: "1em" }}
            >
              <option value="">Select violation</option>
              {VIOLATION_TYPES.map(v => (
                <option key={v.value} value={v.value}>{v.label}</option>
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
              src={`http://${host}:${port}/static/violations/${selectedViolationFile.filename}`}
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

export default CameraFeed;
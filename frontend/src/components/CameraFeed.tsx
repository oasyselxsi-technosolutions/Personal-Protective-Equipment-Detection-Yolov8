import React, { useState } from 'react';
import { cameraFeeds, CameraFeedConfig } from '../config/cameraFeedConfig';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

function formatTime(t: string) {
  if (!t) return "--:--";
  const [h, m] = t.split(":");
  let hour = parseInt(h, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  hour = hour % 12 || 12;
  return `${hour.toString().padStart(2, "0")}:${m} ${ampm}`;
}

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

const timeOptions = generateTimeOptions(30);

function getToday() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

const CameraFeed: React.FC = () => {
  const [selectedFeed, setSelectedFeed] = useState<CameraFeedConfig | null>(cameraFeeds[0]);
  const [imgKey, setImgKey] = useState(Date.now());
  const [showFeed, setShowFeed] = useState(true);
  const [date, setDate] = useState(getToday());
  const [timeRange, setTimeRange] = useState({ from: '07:00', to: '08:00' });
  const [feedError, setFeedError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Compose the time range string for display
  const timeRangeDisplay =
    timeRange.from && timeRange.to
      ? `${formatTime(timeRange.from)} - ${formatTime(timeRange.to)}`
      : "Select time range";

  // Handle feed selection and reset error (WebCamFeed.tsx pattern)
  const handleFeedSelect = async (feed: CameraFeedConfig) => {
    if (selectedFeed && selectedFeed.id !== feed.id) {
      setShowFeed(false);
      setLoading(true);
      try {
        await fetch(`${API_BASE_URL}/release_feed`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ feed_type: selectedFeed.type })
        });
      } catch (e) {
        setFeedError("Failed to release previous feed. Please check backend.");
      }
      setTimeout(() => {
        setSelectedFeed(feed);
        setFeedError(null);
        setImgKey(Date.now());
        setShowFeed(true);
        setLoading(false);
      }, 500);
    } else {
      setSelectedFeed(feed);
      setFeedError(null);
      setImgKey(Date.now());
      setShowFeed(true);
    }
  };

  // Error handlers for image/video
  const handleImgError = () => {
    setFeedError(
      "Unable to connect to the server or stream. Please ensure the backend is running and the feed is available."
    );
  };

  const handleVideoError = () => {
    setFeedError(
      "Unable to connect to the server or stream. Please ensure the backend is running and the feed is available."
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f7f7fa' }}>
      {/* Sidebar: Camera Feed List */}
      <div style={{ width: 250, background: '#fff', padding: 16, borderRadius: 12, margin: 16 }}>
        <h3 style={{ margin: '0 0 16px 0' }}>Feed</h3>
        {cameraFeeds.map(feed => (
          <div
            key={feed.id}
            style={{
              marginBottom: 16,
              cursor: loading ? 'wait' : 'pointer',
              background: selectedFeed?.id === feed.id ? '#e6f0fa' : 'transparent',
              borderRadius: 8,
              padding: 8,
              display: 'flex',
              alignItems: 'center',
              opacity: loading ? 0.5 : 1
            }}
            onClick={() => !loading && handleFeedSelect(feed)}
          >
            <div>
              <div style={{ fontWeight: 600 }}>{feed.name}</div>
              <div style={{ fontSize: 12, color: '#888' }}>{feed.location}</div>
            </div>
          </div>
        ))}
      </div>
      {/* Main Content */}
      <div style={{ flex: 1, padding: 24 }}>
        {/* Top Bar */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
          <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          <span style={{ margin: '0 8px' }}>Time:</span>
          <select
            value={timeRange.from}
            onChange={e => setTimeRange({ ...timeRange, from: e.target.value })}
            style={{ marginRight: 8 }}
          >
            {timeOptions.map(t => (
              <option key={t} value={t}>{formatTime(t)}</option>
            ))}
          </select>
          <span style={{ margin: '0 8px' }}>to</span>
          <select
            value={timeRange.to}
            onChange={e => setTimeRange({ ...timeRange, to: e.target.value })}
            style={{ marginRight: 8 }}
          >
            {timeOptions.map(t => (
              <option key={t} value={t}>{formatTime(t)}</option>
            ))}
          </select>
          <span style={{ fontWeight: 500, color: "#555", marginLeft: 8 }}>
            {timeRangeDisplay}
          </span>
        </div>
        {/* Video Area */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 16, minHeight: 400 }}>
          {selectedFeed ? (
            showFeed && (selectedFeed.type === 'webcam' ? (
              <img
                key={imgKey}
                src={selectedFeed.url}
                alt={selectedFeed.name}
                style={{ width: '100%', borderRadius: 8, maxHeight: 500, objectFit: 'contain' }}
                onError={handleImgError}
              />
            ) : (
              <video
                key={imgKey}
                src={selectedFeed.url}
                controls
                style={{ width: '100%', borderRadius: 8, maxHeight: 500, objectFit: 'contain' }}
                onError={handleVideoError}
              />
            ))
          ) : (
            <div style={{ color: '#888', textAlign: 'center', padding: 40 }}>
              Select a camera feed to view.
            </div>
          )}
          {feedError && (
            <div style={{ color: 'red', marginTop: 16, fontWeight: 500 }}>
              {feedError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
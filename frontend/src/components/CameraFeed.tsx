import React, { useState, useEffect } from 'react';
import { cameraFeeds, CameraFeedConfig } from '../config/cameraFeedConfig';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

interface CameraFeedProps {
  onDateTimeChange?: (date: string, timeRange: { from: string; to: string }) => void;
}

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


const CameraFeed: React.FC<CameraFeedProps> = ({ onDateTimeChange }) => {
  const [selectedFeed, setSelectedFeed] = useState<CameraFeedConfig | null>(cameraFeeds[0]);
  const [imgKey, setImgKey] = useState(Date.now());
  const [showFeed, setShowFeed] = useState(true);
  const [date, setDate] = useState(getToday());
  const [timeRange, setTimeRange] = useState({ from: '07:00', to: '08:00' });
  const [feedError, setFeedError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [violationRecordingEnabled, setViolationRecordingEnabled] = useState<boolean>(false);
  // Fetch violation recording enabled status on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/violation_recording_status`)
      .then(res => res.json())
      .then(data => {
        setViolationRecordingEnabled(!!data.violation_recording_enabled);
        console.log('[CameraFeed] violation_recording_enabled:', data.violation_recording_enabled);
      })
      .catch(err => {
        setViolationRecordingEnabled(false);
        console.error('[CameraFeed] Failed to fetch violation_recording_enabled:', err);
      });
  }, []);

  // Notify parent component when date/time changes
  useEffect(() => {
    console.log('[DEBUG] CameraFeed date/time changed:', { date, timeRange });
    if (onDateTimeChange) {
      console.log('[DEBUG] CameraFeed calling onDateTimeChange callback');
      onDateTimeChange(date, timeRange);
    } else {
      console.log('[DEBUG] CameraFeed no onDateTimeChange callback provided');
    }
  }, [date, timeRange, onDateTimeChange]);

  // Component initialization logging
  useEffect(() => {
    console.log('🎥 [CameraFeed] Component mounted');
    console.log('🎥 [CameraFeed] Available camera feeds:', cameraFeeds.length);
    console.log('🎥 [CameraFeed] Camera feeds configuration:', cameraFeeds);
    console.log('🎥 [CameraFeed] API Base URL:', API_BASE_URL);
    console.log('🎥 [CameraFeed] Default selected feed:', cameraFeeds[0]);
    
    // Log healthcare feed specifically (check both webcam and ipcamera versions)
    const healthcareFeed = cameraFeeds.find(feed => 
      feed.id === 'webcam_healthcare' || feed.id === 'ipcamera_healthcare' || 
      feed.name.toLowerCase().includes('healthcare')
    );
    if (healthcareFeed) {
      console.log('🏥 [CameraFeed] Healthcare feed found:', healthcareFeed);
      console.log('🏥 [CameraFeed] Healthcare URL to be used:', healthcareFeed.url);
      
      // Test the healthcare URL directly
      fetch(healthcareFeed.url, { method: 'HEAD' })
        .then(response => {
          console.log('🏥 [CameraFeed] Healthcare URL HEAD test:', {
            status: response.status,
            contentType: response.headers.get('Content-Type'),
            url: healthcareFeed.url
          });
        })
        .catch(error => {
          console.error('🏥 [CameraFeed] Healthcare URL HEAD test failed:', error);
        });
    } else {
      console.warn('⚠️ [CameraFeed] Healthcare feed not found in configuration!');
      console.log('🔍 [CameraFeed] Available feed IDs:', cameraFeeds.map(f => f.id));
    }
  }, []);

  // Compose the time range string for display
  const timeRangeDisplay =
    timeRange.from && timeRange.to
      ? `${formatTime(timeRange.from)} - ${formatTime(timeRange.to)}`
      : "Select time range";

  // Handle feed selection and reset error (WebCamFeed.tsx pattern)
  const handleFeedSelect = async (feed: CameraFeedConfig) => {
    console.log(`🎥 [CameraFeed] Selecting feed:`, {
      id: feed.id,
      name: feed.name,
      url: feed.url,
      type: feed.type,
      location: feed.location
    });

    if (selectedFeed && selectedFeed.id !== feed.id) {
      console.log(`🔄 [CameraFeed] Switching from ${selectedFeed.name} to ${feed.name}`);
      setShowFeed(false);
      setLoading(true);
      try {
        console.log(`🔌 [CameraFeed] Releasing previous feed of type: ${selectedFeed.type}`);
        const response = await fetch(`${API_BASE_URL}/release_feed`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ feed_type: selectedFeed.type })
        });
        
        if (response.ok) {
          console.log(`✅ [CameraFeed] Successfully released previous feed`);
        } else {
          console.warn(`⚠️ [CameraFeed] Release feed returned status: ${response.status}`);
        }
      } catch (e) {
        console.error(`❌ [CameraFeed] Failed to release previous feed:`, e);
        // Don't show error to user for release_feed failures - it's not critical
        // The new feed should still work even if release fails
        console.log(`🔄 [CameraFeed] Continuing with feed switch despite release error`);
      }
      setTimeout(() => {
        console.log(`⏰ [CameraFeed] Loading new feed after delay: ${feed.name}`);
        setSelectedFeed(feed);
        setFeedError(null);
        setImgKey(Date.now());
        setShowFeed(true);
        setLoading(false);
      }, 500);
    } else {
      console.log(`🚀 [CameraFeed] Loading feed directly: ${feed.name}`);
      setSelectedFeed(feed);
      setFeedError(null);
      setImgKey(Date.now());
      setShowFeed(true);
    }
  };

  // Handle recording toggle
  const handleRecordingToggle = async () => {
    // Use violationRecordingEnabled to determine action, not local recording state
    const action = violationRecordingEnabled ? 'stop' : 'start';
    const endpoint = violationRecordingEnabled
      ? `${API_BASE_URL}/stop_violation_recording`
      : `${API_BASE_URL}/start_violation_recording`;

    console.log(`🎬 [CameraFeed] Attempting to ${action} violation recording`);
    console.log(`🎬 [CameraFeed] Endpoint: ${endpoint}`);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log(`🎬 [CameraFeed] Response status: ${response.status}`);

      if (response.ok) {
        const result = await response.json().catch(() => ({}));
        console.log(`✅ [CameraFeed] Successfully ${action}ed violation recording`, result);
        // Update violationRecordingEnabled to reflect backend state
        setViolationRecordingEnabled(!violationRecordingEnabled);
        // Optionally update local recording state for legacy logic
        setRecording(!violationRecordingEnabled);

        // Show success message
        const message = !violationRecordingEnabled ? 'Violation recording started' : 'Violation recording stopped';
        console.log(`🎬 [CameraFeed] ${message}`);
      } else {
        const errorText = await response.text().catch(() => 'Unknown error');
        console.error(`❌ [CameraFeed] Failed to ${action} recording: ${response.status} - ${errorText}`);
        alert(`Failed to ${action} violation recording: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error(`❌ [CameraFeed] Network error during ${action} recording:`, error);
      alert(`Failed to ${action} violation recording. Please check if the backend is running.`);
    }
  };

  // Error handler for image/stream
  const handleImgError = () => {
    const errorMessage = `Unable to connect to ${selectedFeed?.name || 'camera'} feed. Please ensure the backend is running and the camera is accessible.`;
    console.error(`❌ [CameraFeed] Image load error:`, {
      feedName: selectedFeed?.name,
      feedUrl: selectedFeed?.url,
      feedType: selectedFeed?.type,
      errorMessage
    });
    setFeedError(errorMessage);
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

          {/* Recording Button (always visible, color/label based on violationRecordingEnabled) */}
          <button
            onClick={handleRecordingToggle}
            style={{
              padding: "0.5em 1.5em",
              borderRadius: "8px",
              background: violationRecordingEnabled ? "#d32f2f" : "#43a047", // Red if enabled, Green if not
              color: "#fff",
              border: "none",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: "14px",
              transition: "background-color 0.2s ease",
              marginRight: "24px"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = violationRecordingEnabled ? "#b71c1c" : "#388e3c"; // Darker red/green on hover
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = violationRecordingEnabled ? "#d32f2f" : "#43a047";
            }}
          >
            {violationRecordingEnabled ? "Stop Recording Violations" : "Start Recording Violations"}
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center' }}>
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
        </div>
        {/* Video Area */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 16, minHeight: 400 }}>
          {selectedFeed ? (
            showFeed && (
              // All camera feeds (webcam and ipcamera) are MJPEG streams, so use img tag
              <img
                key={imgKey}
                src={selectedFeed.url}
                alt={selectedFeed.name}
                style={{ 
                  width: '100%', 
                  borderRadius: 8, 
                  maxHeight: 500, 
                  objectFit: 'contain',
                  border: '1px solid #ddd'
                }}
                onError={handleImgError}
                onLoad={() => {
                  console.log(`✅ [CameraFeed] Successfully loaded feed:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url,
                    type: selectedFeed.type,
                    timestamp: new Date().toISOString()
                  });
                  setFeedError(null);
                }}
                onLoadStart={() => {
                  console.log(`🔄 [CameraFeed] Starting to load feed:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url
                  });
                }}
                onAbort={() => {
                  console.warn(`⚠️ [CameraFeed] Feed load aborted:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url
                  });
                }}
                onStalled={() => {
                  console.warn(`⏸️ [CameraFeed] Feed load stalled:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url
                  });
                }}
                onSuspend={() => {
                  console.warn(`⏸️ [CameraFeed] Feed load suspended:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url
                  });
                }}
                onProgress={() => {
                  console.log(`📊 [CameraFeed] Feed loading progress:`, {
                    name: selectedFeed.name,
                    url: selectedFeed.url
                  });
                }}
              />
            )
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
          {loading && (
            <div style={{ color: '#007bff', marginTop: 16, fontWeight: 500 }}>
              Loading feed...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
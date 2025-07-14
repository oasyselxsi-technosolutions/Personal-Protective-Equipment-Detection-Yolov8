import React, { useEffect, useState } from 'react';
import axios from 'axios';

// Helper functions for time formatting and generation
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

interface DashboardData {
  overall_compliance: number;
  ppe_compliance: Record<string, number>;
  ppe_alerts: Record<string, number>;
  alerts: number[];
  violation_over_time: number[];
}

interface ViolationImage {
  id: string;
  filename: string;
  timestamp: string;
  violation_type: string;
  confidence: number;
  camera_location?: string;
  file_path: string;
  thumbnail_path?: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [violationImages, setViolationImages] = useState<ViolationImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<ViolationImage | null>(null);
  const [violationsLoading, setViolationsLoading] = useState<boolean>(false);
  const [violationsError, setViolationsError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(getToday());
  const [selectedTimeRange, setSelectedTimeRange] = useState<{ from: string; to: string }>({ from: '07:00', to: '08:00' });

  useEffect(() => {
    // Load initial dashboard data
    axios.get<DashboardData>(`${API_BASE_URL}/dashboard`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Dashboard data load error:', err);
        setError('Failed to load dashboard data');
        setLoading(false);
      });
  }, []);

  // Function to fetch violation images based on date/time filters
  const fetchViolationImages = async (date?: string, timeRange?: { from: string; to: string }) => {
    console.log('[DEBUG] Dashboard fetchViolationImages called with:', { date, timeRange });
    setViolationsLoading(true);
    setViolationsError(null);
    
    try {
      const params = new URLSearchParams();
      
      if (date) {
        console.log('[DEBUG] Dashboard adding date filter:', date);
        params.append('date', date);
      }
      if (timeRange?.from) {
        console.log('[DEBUG] Dashboard adding time_from filter:', timeRange.from);
        params.append('time_from', timeRange.from);
      }
      if (timeRange?.to) {
        console.log('[DEBUG] Dashboard adding time_to filter:', timeRange.to);
        params.append('time_to', timeRange.to);
      }

      const apiUrl = `${API_BASE_URL}/violation_images?${params.toString()}`;
      console.log('🔍 [Dashboard] Fetching violations from URL:', apiUrl);
      console.log('🔍 [Dashboard] Full params string:', params.toString());
      
      const response = await axios.get<ViolationImage[]>(apiUrl);
      
      console.log('📸 [Dashboard] API Response status:', response.status);
      console.log('📸 [Dashboard] API Response data type:', typeof response.data);
      console.log('📸 [Dashboard] Fetched violation images count:', response.data.length);
      console.log('📸 [Dashboard] First few images:', response.data.slice(0, 3));
      
      setViolationImages(response.data);
      
      // Auto-select first image if available
      if (response.data.length > 0) {
        console.log('[DEBUG] Dashboard auto-selecting first image:', response.data[0].filename);
        setSelectedImage(response.data[0]);
      } else {
        console.log('[DEBUG] Dashboard no images found, clearing selection');
        setSelectedImage(null);
      }
      
    } catch (err: any) {
      console.error('❌ [Dashboard] Error fetching violation images:', err);
      console.error('❌ [Dashboard] Error details:', {
        message: err?.message || 'Unknown error',
        response: err?.response?.data,
        status: err?.response?.status,
        url: err?.config?.url
      });
      setViolationsError('Failed to load violation images');
      setViolationImages([]);
      setSelectedImage(null);
    } finally {
      setViolationsLoading(false);
    }
  };

  // Load violations when date/time changes
  useEffect(() => {
    console.log('[DEBUG] Dashboard useEffect triggered for violations:', { selectedDate, selectedTimeRange });
    if (selectedDate || (selectedTimeRange.from && selectedTimeRange.to)) {
      console.log('[DEBUG] Dashboard calling fetchViolationImages with filters');
      fetchViolationImages(selectedDate, selectedTimeRange);
    } else {
      console.log('[DEBUG] Dashboard no valid filters, skipping API call');
    }
  }, [selectedDate, selectedTimeRange]);

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getImageUrl = (imagePath: string) => {
    // Construct full URL for the image
    return `${API_BASE_URL.replace('/api', '')}/violations/${imagePath}`;
  };

  if (loading) return <div style={{ padding: 20 }}>Loading dashboard...</div>;
  if (error) return <div style={{ color: 'red', padding: 20 }}>{error}</div>;

  return (
    <div style={{ background: '#f7f7fa', minHeight: '100vh' }}>
      {/* Dashboard Stats Header */}
      <div style={{ padding: '20px 24px', background: '#fff', borderBottom: '1px solid #e0e0e0' }}>
        <h2 style={{ margin: '0 0 16px 0', color: '#333' }}>Safety Monitoring Dashboard</h2>
        {data && (
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div style={{ 
              background: '#e8f5e8', 
              padding: 16, 
              borderRadius: 8, 
              minWidth: 200,
              border: '1px solid #c8e6c9'
            }}>
              <div style={{ fontSize: 14, color: '#2e7d32', fontWeight: 600 }}>Overall Compliance</div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1b5e20' }}>{data.overall_compliance}%</div>
            </div>
            <div style={{ 
              background: '#fff3e0', 
              padding: 16, 
              borderRadius: 8, 
              minWidth: 200,
              border: '1px solid #ffcc02'
            }}>
              <div style={{ fontSize: 14, color: '#ef6c00', fontWeight: 600 }}>Total Alerts</div>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#e65100' }}>
                {Object.values(data.ppe_alerts).reduce((sum, val) => sum + val, 0)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Date & Time Selection Section */}
      <div style={{ margin: 24 }}>
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#333', display: 'flex', alignItems: 'center', gap: 8 }}>
            📅 Select Date & Time Range
          </h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
            {/* Date Input */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontWeight: 600, color: '#555' }}>Date:</label>
              <input 
                type="date" 
                value={selectedDate} 
                onChange={(e) => {
                  console.log('[DEBUG] Dashboard date changed:', e.target.value);
                  setSelectedDate(e.target.value);
                }}
                style={{
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>

            {/* Time Range Inputs */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontWeight: 600, color: '#555' }}>Time:</label>
              <select
                value={selectedTimeRange.from}
                onChange={(e) => {
                  console.log('[DEBUG] Dashboard time_from changed:', e.target.value);
                  setSelectedTimeRange({ ...selectedTimeRange, from: e.target.value });
                }}
                style={{
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                {timeOptions.map(t => (
                  <option key={t} value={t}>{formatTime(t)}</option>
                ))}
              </select>
              
              <span style={{ color: '#666', fontWeight: 500 }}>to</span>
              
              <select
                value={selectedTimeRange.to}
                onChange={(e) => {
                  console.log('[DEBUG] Dashboard time_to changed:', e.target.value);
                  setSelectedTimeRange({ ...selectedTimeRange, to: e.target.value });
                }}
                style={{
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                {timeOptions.map(t => (
                  <option key={t} value={t}>{formatTime(t)}</option>
                ))}
              </select>
            </div>

            {/* Time Range Display */}
            <div style={{ 
              background: '#e3f2fd', 
              color: '#1976d2', 
              padding: '8px 12px', 
              borderRadius: '6px',
              fontWeight: 500,
              fontSize: '14px'
            }}>
              {selectedTimeRange.from && selectedTimeRange.to
                ? `${formatTime(selectedTimeRange.from)} - ${formatTime(selectedTimeRange.to)}`
                : "Select time range"}
            </div>
          </div>
          
          {/* Current Selection Summary */}
          <div style={{ 
            marginTop: 16, 
            padding: 12, 
            background: '#f5f5f5', 
            borderRadius: 6,
            fontSize: 13,
            color: '#666'
          }}>
            <strong>Current Selection:</strong> {selectedDate} from {formatTime(selectedTimeRange.from)} to {formatTime(selectedTimeRange.to)}
          </div>
        </div>
      </div>

      {/* Violations Listing Section */}
      <div style={{ margin: 24 }}>
        <div style={{ background: '#fff', borderRadius: 12, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          {/* Violations Header */}
          <div style={{ 
            padding: '16px 20px', 
            borderBottom: '1px solid #e0e0e0',
            background: '#fafafa'
          }}>
            <h3 style={{ margin: 0, color: '#333', display: 'flex', alignItems: 'center', gap: 8 }}>
              🚨 Violation Images
              {violationImages.length > 0 && (
                <span style={{ 
                  background: '#ff5252', 
                  color: 'white', 
                  padding: '2px 8px', 
                  borderRadius: 12, 
                  fontSize: 12,
                  fontWeight: 600
                }}>
                  {violationImages.length}
                </span>
              )}
            </h3>
            {selectedDate && (
              <div style={{ fontSize: 14, color: '#666', marginTop: 4 }}>
                Date: {selectedDate} | Time: {selectedTimeRange.from} - {selectedTimeRange.to}
              </div>
            )}
            <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
              [DEBUG] Current filters: date="{selectedDate}", from="{selectedTimeRange.from}", to="{selectedTimeRange.to}"
            </div>
          </div>

          {/* Violations Content */}
          <div style={{ padding: 20 }}>
            {violationsLoading ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#666' }}>
                Loading violation images...
              </div>
            ) : violationsError ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#d32f2f' }}>
                {violationsError}
              </div>
            ) : violationImages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#666' }}>
                No violations found for the selected date and time range.
                <br />
                <small style={{ color: '#999' }}>Select a date and time range from the camera feed above to view violations.</small>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: 20, minHeight: 400 }}>
                {/* File List (Left Side) */}
                <div style={{ 
                  width: 350, 
                  border: '1px solid #e0e0e0', 
                  borderRadius: 8,
                  background: '#fafafa'
                }}>
                  <div style={{ 
                    padding: 12, 
                    borderBottom: '1px solid #e0e0e0', 
                    background: '#f5f5f5',
                    fontWeight: 600,
                    fontSize: 14
                  }}>
                    Violation Files ({violationImages.length})
                  </div>
                  <div style={{ 
                    maxHeight: 350, 
                    overflowY: 'auto',
                    padding: 8
                  }}>
                    {violationImages.map((image, index) => (
                      <div
                        key={image.id || index}
                        style={{
                          padding: 12,
                          marginBottom: 4,
                          borderRadius: 6,
                          cursor: 'pointer',
                          background: selectedImage?.id === image.id ? '#e3f2fd' : '#fff',
                          border: selectedImage?.id === image.id ? '2px solid #1976d2' : '1px solid #e0e0e0',
                          transition: 'all 0.2s ease'
                        }}
                        onClick={() => setSelectedImage(image)}
                        onMouseOver={(e) => {
                          if (selectedImage?.id !== image.id) {
                            e.currentTarget.style.background = '#f5f5f5';
                          }
                        }}
                        onMouseOut={(e) => {
                          if (selectedImage?.id !== image.id) {
                            e.currentTarget.style.background = '#fff';
                          }
                        }}
                      >
                        <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, color: '#333' }}>
                          {image.filename}
                        </div>
                        <div style={{ fontSize: 12, color: '#666', marginBottom: 2 }}>
                          {formatTimestamp(image.timestamp)}
                        </div>
                        <div style={{ fontSize: 12, marginBottom: 2 }}>
                          <span style={{ 
                            background: '#ffebee', 
                            color: '#c62828', 
                            padding: '2px 6px', 
                            borderRadius: 4,
                            fontSize: 11,
                            fontWeight: 600
                          }}>
                            {image.violation_type}
                          </span>
                          {image.confidence && (
                            <span style={{ 
                              marginLeft: 6,
                              color: '#666',
                              fontSize: 11
                            }}>
                              {Math.round(image.confidence * 100)}%
                            </span>
                          )}
                        </div>
                        {image.camera_location && (
                          <div style={{ fontSize: 11, color: '#888' }}>
                            📍 {image.camera_location}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Image Preview (Right Side) */}
                <div style={{ 
                  flex: 1, 
                  border: '1px solid #e0e0e0', 
                  borderRadius: 8,
                  background: '#fff',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  <div style={{ 
                    padding: 12, 
                    borderBottom: '1px solid #e0e0e0', 
                    background: '#f5f5f5',
                    fontWeight: 600,
                    fontSize: 14
                  }}>
                    Image Preview
                  </div>
                  <div style={{ 
                    flex: 1, 
                    padding: 16,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {selectedImage ? (
                      <>
                        <img
                          src={getImageUrl(selectedImage.file_path)}
                          alt={selectedImage.filename}
                          style={{
                            maxWidth: '100%',
                            maxHeight: 300,
                            objectFit: 'contain',
                            borderRadius: 8,
                            border: '1px solid #ddd',
                            marginBottom: 16
                          }}
                          onError={(e) => {
                            console.error('❌ [Dashboard] Image load error:', selectedImage.file_path);
                            e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmNWY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBmb3VuZDwvdGV4dD48L3N2Zz4=';
                          }}
                        />
                        <div style={{ textAlign: 'center', width: '100%' }}>
                          <div style={{ fontWeight: 600, marginBottom: 8, color: '#333' }}>
                            {selectedImage.filename}
                          </div>
                          <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>
                            {formatTimestamp(selectedImage.timestamp)}
                          </div>
                          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <span style={{ 
                              background: '#ffebee', 
                              color: '#c62828', 
                              padding: '4px 8px', 
                              borderRadius: 4,
                              fontSize: 12,
                              fontWeight: 600
                            }}>
                              {selectedImage.violation_type}
                            </span>
                            {selectedImage.confidence && (
                              <span style={{ 
                                background: '#e8f5e8', 
                                color: '#2e7d32', 
                                padding: '4px 8px', 
                                borderRadius: 4,
                                fontSize: 12,
                                fontWeight: 600
                              }}>
                                {Math.round(selectedImage.confidence * 100)}% Confidence
                              </span>
                            )}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div style={{ textAlign: 'center', color: '#999' }}>
                        <div style={{ fontSize: 48, marginBottom: 16 }}>📷</div>
                        <div>Select an image from the list to preview</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
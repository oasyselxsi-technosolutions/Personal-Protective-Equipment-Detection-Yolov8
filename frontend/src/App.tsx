import React, { useState } from 'react';
import * as FaIcons from 'react-icons/fa';
import Dashboard from './components/Dashboard';
import CameraFeed from './components/CameraFeed';
import Reports from './components/Reports';
import WebCamFeed from './components/WebCamFeed';

type MenuItem = {
  label: string;
  icon: 'dashboard' | 'camera' | 'webcam' | 'reports';
};

const MENU: MenuItem[] = [
  { label: 'Dashboard', icon: 'dashboard' },
  { label: 'Camera Feed', icon: 'camera' },
  { label: 'WebCam Feed', icon: 'webcam' }, // New menu item
  { label: 'Reports', icon: 'reports' },
];

const ICON_MAP: Record<MenuItem['icon'], React.ReactElement> = {
  dashboard: React.createElement((FaIcons.FaTachometerAlt as any).default || FaIcons.FaTachometerAlt, { size: 20 }),
  camera: React.createElement((FaIcons.FaVideo as any).default || FaIcons.FaVideo, { size: 20 }),
  webcam: React.createElement((FaIcons.FaCamera as any).default || FaIcons.FaCamera, { size: 20 }), // Icon for webcam
  reports: React.createElement((FaIcons.FaFileAlt as any).default || FaIcons.FaFileAlt, { size: 20 }),
};

const App: React.FC = () => {
  const [selected, setSelected] = useState('Dashboard');

  const renderContent = () => {
    switch (selected) {
      case 'Dashboard':
        return <Dashboard />;
      case 'Camera Feed':
        return <CameraFeed />;
      case 'WebCam Feed':
        return <WebCamFeed />;
      case 'Reports':
        return <Reports />;
      default:
        return null;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f7f7fa' }}>
      {/* Sidebar */}
      <div style={{
        width: 220,
        background: '#fff',
        boxShadow: '2px 0 8px #f0f1f2',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        padding: '2rem 0 2rem 1rem'
      }}>
        <div style={{ marginBottom: '2rem', fontWeight: 'bold', fontSize: 18, color: '#888' }}>
          Industrial Safety AI
        </div>
        {MENU.map(item => (
          <button
            key={item.label}
            onClick={() => setSelected(item.label)}
            style={{
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              padding: '0.75rem 1rem',
              marginBottom: '0.5rem',
              background: selected === item.label ? '#e6f0fa' : 'transparent',
              border: 'none',
              borderRadius: 8,
              color: selected === item.label ? '#1976d2' : '#333',
              fontWeight: selected === item.label ? 'bold' : 'normal',
              fontSize: 16,
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <span style={{ marginRight: 12, fontSize: 20 }}>
              {ICON_MAP[item.icon]}
            </span>
            {item.label}
          </button>
        ))}
        <div style={{ flexGrow: 1 }} />
        <div style={{ fontSize: 12, color: '#bbb', marginLeft: 8, marginTop: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
            <span>Powered by</span>
            <img
              src="/oasys-logo.png"
              alt="Oasys Elxsi Techno Solutions"
              style={{ height: 46, marginLeft: 8 }}
            />
          </div>
          <div style={{ marginTop: 4, fontWeight: 'bold', color: '#888', textAlign: 'left' }}>
            Oasys Elxsi Techno Solutions
          </div>
        </div>
      </div>
      {/* Main Content */}
      <div style={{ flex: 1, padding: '2rem 2rem 2rem 2rem' }}>
        <div style={{ fontSize: 28, fontWeight: 700, color: '#6c648b', marginBottom: 24 }}>
          Dashboard : Industrial Safety AI
        </div>
        <div>
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default App;
import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

type Violation = {
  type: string;
  location: string;
  timestamp: string;
};

const ViolationAlert: React.FC = () => {
  const [alerts, setAlerts] = useState<Violation[]>([]);

  useEffect(() => {
    socket.on('violation_alert', (violation: Violation) => {
      setAlerts(prev => [violation, ...prev]);
    });
    return () => {
      socket.off('violation_alert');
    };
  }, []);

  return (
    <div style={{ position: 'fixed', top: 20, right: 20, zIndex: 1000 }}>
      {alerts.map((alert, idx) => (
        <div key={idx} style={{ background: '#ffeb3b', margin: 8, padding: 12, borderRadius: 6, boxShadow: '0 2px 8px #888' }}>
          <b>{alert.type}</b> at <b>{alert.location}</b> <span style={{ fontSize: 12, color: '#555' }}>({alert.timestamp})</span>
        </div>
      ))}
    </div>
  );
};

export default ViolationAlert;

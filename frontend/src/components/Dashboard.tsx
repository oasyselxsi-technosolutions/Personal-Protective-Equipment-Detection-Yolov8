import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface DashboardData {
  overall_compliance: number;
  ppe_compliance: Record<string, number>;
  ppe_alerts: Record<string, number>;
  alerts: number[];
  violation_over_time: number[];
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios.get<DashboardData>('http://localhost:5000/api/dashboard')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load dashboard data');
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!data) return <div>No data available.</div>;

  return (
    <div>
      <h2>Dashboard</h2>
      <div>Overall Compliance: {data.overall_compliance}%</div>
      <div>
        <h3>PPE Compliance:</h3>
        <ul>
          {Object.entries(data.ppe_compliance).map(([k, v]) => (
            <li key={k}>{k}: {v}%</li>
          ))}
        </ul>
      </div>
      <div>
        <h3>PPE Alerts:</h3>
        <ul>
          {Object.entries(data.ppe_alerts).map(([k, v]) => (
            <li key={k}>{k}: {v}</li>
          ))}
        </ul>
      </div>
      {/* Add charts and more UI as needed */}
    </div>
  );
};

export default Dashboard;
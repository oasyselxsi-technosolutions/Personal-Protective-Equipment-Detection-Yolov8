import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ReportRow {
  date: string;
  helmet: number;
  boots: number;
  glasses: number;
  mask: number;
  gloves: number;
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<ReportRow[]>([]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/reports')
      .then(res => setReports(res.data));
  }, []);

  return (
    <div>
      <h2>Reports</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>Helmet</th><th>Boots</th><th>Glasses</th><th>Mask</th><th>Gloves</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((row, idx) => (
            <tr key={idx}>
              <td>{row.date}</td>
              <td>{row.helmet}</td>
              <td>{row.boots}</td>
              <td>{row.glasses}</td>
              <td>{row.mask}</td>
              <td>{row.gloves}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <a href="http://localhost:5000/api/download_report" target="_blank" rel="noopener noreferrer">
        Download Report
      </a>
    </div>
  );
};

export default Reports;
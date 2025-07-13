import React, { useEffect, useState } from 'react';
import axios from 'axios';

// Helper to get today's date in YYYY-MM-DD format
function getToday() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

const Reports: React.FC = () => {
  const [tab, setTab] = useState<'domain' | 'timeline' | 'recent' | 'type'>('domain');
  const [date, setDate] = useState('');
  const [counts, setCounts] = useState<{ domain: string, count: number }[]>([]);
  const [timelineFrom, setTimelineFrom] = useState('');
  const [timelineTo, setTimelineTo] = useState('');
  const [timeline, setTimeline] = useState<{ date: string, count: number }[]>([]);
  const [recentLimit, setRecentLimit] = useState(10);
  const [recent, setRecent] = useState<any[]>([]);
  const [typeCounts, setTypeCounts] = useState<{ type: string, count: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Set today's date as default on mount
  useEffect(() => {
    const today = getToday();
    setDate(today);
    setTimelineFrom(today);
    setTimelineTo(today);
  }, []);

  // Fetch domain counts
  useEffect(() => {
    if (tab === 'domain' && date) {
      axios.get(`http://localhost:5000/api/violations/count?date=${date}`)
        .then(res => {
          setCounts(res.data);
          setError(null);
        })
        .catch(() => setError("Unable to connect to the server. Please ensure the backend is running."));
    }
  }, [tab, date]);

  // Fetch timeline data
  useEffect(() => {
    if (tab === 'timeline' && timelineFrom && timelineTo && timelineFrom <= timelineTo) {
      axios.get(`http://localhost:5000/api/violations/timeline?from=${timelineFrom}&to=${timelineTo}`)
        .then(res => {
          setTimeline(res.data);
          setError(null);
        })
        .catch(() => setError("Unable to connect to the server. Please ensure the backend is running."));
    }
  }, [tab, timelineFrom, timelineTo]);

  // Fetch recent violations
  useEffect(() => {
    if (tab === 'recent') {
      axios.get(`http://localhost:5000/api/violations/recent?limit=${recentLimit}`)
        .then(res => {
          setRecent(res.data);
          setError(null);
        })
        .catch(() => setError("Unable to connect to the server. Please ensure the backend is running."));
    }
  }, [tab, recentLimit]);

  // Fetch by type
  useEffect(() => {
    if (tab === 'type' && date) {
      axios.get(`http://localhost:5000/api/violations/by_type?date=${date}`)
        .then(res => {
          setTypeCounts(res.data);
          setError(null);
        })
        .catch(() => setError("Unable to connect to the server. Please ensure the backend is running."));
    }
  }, [tab, date]);

  // Export CSV for current tab
  const exportCSV = () => {
    let csv = '';
    if (tab === 'domain') {
      csv = "Domain,Count\n" + counts.map(c => `${c.domain},${c.count}`).join("\n");
    } else if (tab === 'timeline') {
      csv = "Date,Count\n" + timeline.map(t => `${t.date},${t.count}`).join("\n");
    } else if (tab === 'type') {
      csv = "Type,Count\n" + typeCounts.map(t => `${t.type},${t.count}`).join("\n");
    } else {
      csv = "Domain,Timestamp,Filename\n" + recent.map(r => `${r.domain},${r.timestamp},${r.filename}`).join("\n");
    }
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = tab === 'domain'
      ? `violation_counts_${date}.csv`
      : tab === 'timeline'
      ? `violation_timeline_${timelineFrom}_to_${timelineTo}.csv`
      : tab === 'type'
      ? `violation_types_${date}.csv`
      : `recent_violations.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Improved BarChart component for timeline visualization
  const BarChart: React.FC<{ data: { date: string, count: number }[] }> = ({ data }) => {
    const MAX_BAR_WIDTH = 600; // px
    const maxCount = Math.max(...data.map(d => d.count), 1);
    return (
      <div style={{ width: '100%', padding: 16 }}>
        {data.length === 0 && <div style={{ color: '#aaa' }}>No data for selected range.</div>}
        {data.map((item, idx) => (
          <div key={idx} style={{ marginBottom: 8, display: 'flex', alignItems: 'center' }}>
            <span style={{ display: 'inline-block', width: 100 }}>{item.date}</span>
            <div style={{
              display: 'inline-block',
              background: '#1976d2',
              height: 18,
              width: `${(item.count / maxCount) * MAX_BAR_WIDTH}px`,
              color: '#fff',
              borderRadius: 4,
              textAlign: 'right',
              paddingRight: 8,
              minWidth: 30,
              marginLeft: 8,
              transition: 'width 0.3s'
            }}>{item.count > 0 ? item.count : ''}</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div>
      <h2>Reports</h2>
      {error && (
        <div style={{ color: 'red', marginBottom: 16, fontWeight: 'bold' }}>
          {error}
        </div>
      )}
      <div style={{ marginBottom: 16 }}>
        <button onClick={() => setTab('domain')} style={{ marginRight: 8, fontWeight: tab === 'domain' ? 'bold' : 'normal' }}>By Domain</button>
        <button onClick={() => setTab('timeline')} style={{ marginRight: 8, fontWeight: tab === 'timeline' ? 'bold' : 'normal' }}>Timeline</button>
        <button onClick={() => setTab('type')} style={{ marginRight: 8, fontWeight: tab === 'type' ? 'bold' : 'normal' }}>By Type</button>
        <button onClick={() => setTab('recent')} style={{ fontWeight: tab === 'recent' ? 'bold' : 'normal' }}>Recent Violations</button>
      </div>
      {tab === 'domain' && (
        <div>
          <h3 style={{ marginTop: 24, marginBottom: 8 }}>Violations by Domain (Table)</h3>
          <label>
            Select Date:&nbsp;
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </label>
          <button onClick={exportCSV} style={{ marginLeft: 16 }}>Export CSV</button>
          <table style={{ borderCollapse: 'collapse', width: '100%', marginTop: 16 }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Domain</th>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Violation Count</th>
              </tr>
            </thead>
            <tbody>
              {counts.length === 0 && (
                <tr>
                  <td colSpan={2} style={{ textAlign: 'center', color: '#aaa', padding: 16 }}>
                    No data for selected date.
                  </td>
                </tr>
              )}
              {counts.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.domain}</td>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {tab === 'timeline' && (
        <div>
          <label>
            From:&nbsp;
            <input type="date" value={timelineFrom} onChange={e => setTimelineFrom(e.target.value)} />
          </label>
          <label style={{ marginLeft: 16 }}>
            To:&nbsp;
            <input type="date" value={timelineTo} onChange={e => setTimelineTo(e.target.value)} />
          </label>
          <button onClick={exportCSV} style={{ marginLeft: 16 }}>Export CSV</button>
          <h3 style={{ marginTop: 24, marginBottom: 8 }}>Violations Timeline (Bar Chart)</h3>
          <BarChart data={timeline} />
        </div>
      )}
      {tab === 'type' && (
        <div>
          <h3 style={{ marginTop: 24, marginBottom: 8 }}>Violations by Type (Table)</h3>
          <label>
            Select Date:&nbsp;
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </label>
          <button onClick={exportCSV} style={{ marginLeft: 16 }}>Export CSV</button>
          <table style={{ borderCollapse: 'collapse', width: '100%', marginTop: 16 }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Type</th>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Count</th>
              </tr>
            </thead>
            <tbody>
              {typeCounts.length === 0 && (
                <tr>
                  <td colSpan={2} style={{ textAlign: 'center', color: '#aaa', padding: 16 }}>
                    No data for selected date.
                  </td>
                </tr>
              )}
              {typeCounts.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.type}</td>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {tab === 'recent' && (
        <div>
          <h3 style={{ marginTop: 24, marginBottom: 8 }}>Recent Violations (Table)</h3>
          <label>
            Show&nbsp;
            <select value={recentLimit} onChange={e => setRecentLimit(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
            &nbsp;most recent violations
          </label>
          <button onClick={exportCSV} style={{ marginLeft: 16 }}>Export CSV</button>
          <table style={{ borderCollapse: 'collapse', width: '100%', marginTop: 16 }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Domain</th>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Timestamp</th>
                <th style={{ border: '1px solid #ccc', padding: 8 }}>Filename</th>
              </tr>
            </thead>
            <tbody>
              {recent.length === 0 && (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', color: '#aaa', padding: 16 }}>
                    No recent violations found.
                  </td>
                </tr>
              )}
              {recent.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.domain}</td>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.timestamp}</td>
                  <td style={{ border: '1px solid #ccc', padding: 8 }}>{row.filename}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Reports;
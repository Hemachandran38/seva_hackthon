import { useState, useEffect } from 'react';
import { complaintService } from '../services/complaintService';
import { InfrastructureMap } from '../components/map/InfrastructureMap';
import '../styles/dashboard.css';
import type { Complaint } from '../types/complaint';

export function DashboardPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComplaints = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Use complaintService to get all demo complaints including sample data
        const data = complaintService.getAllComplaints();
        setComplaints(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to fetch complaints';
        setError(message);
        console.error('Dashboard error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComplaints();
  }, []);

  // Calculate metrics
  const metrics = {
    total: complaints.length,
    open: complaints.filter(c => c.status !== 'Resolved').length,
    critical: complaints.filter(c => c.priorityLevel === 'Critical').length,
    resolved: complaints.filter(c => c.status === 'Resolved').length,
  };

  return (
    <div className="dashboard-container">
      {/* Debug Info */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{ padding: '12px', background: '#f0f9ff', border: '1px solid #bfdbfe', borderRadius: '4px', marginBottom: '16px', fontSize: '12px' }}>
          <strong>Debug:</strong> Loaded {complaints.length} complaints. {complaints.filter(c => c.latitude && c.longitude).length} have coordinates.
          {complaints.length > 0 && (
            <>
              <br />First complaint: {complaints[0].id} | Priority: {complaints[0].priorityLevel} | Status: {complaints[0].status} | Lat/Lng: {complaints[0].latitude}/{complaints[0].longitude}
            </>
          )}
        </div>
      )}

      {/* Hero Section */}
      <section className="dashboard-hero">
        <div className="hero-content">
          <h1>Infrastructure Dashboard</h1>
          <p>Real-time view of municipal complaints and infrastructure issues</p>
        </div>
      </section>

      {/* Metrics Cards */}
      {!isLoading && complaints.length > 0 && (
        <section className="dashboard-metrics">
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-number">{metrics.total}</div>
              <div className="metric-label">Total Reports</div>
            </div>
            <div className="metric-item">
              <div className="metric-number">{metrics.open}</div>
              <div className="metric-label">Open Issues</div>
            </div>
            <div className="metric-item">
              <div className="metric-number">{metrics.critical}</div>
              <div className="metric-label">Critical</div>
            </div>
            <div className="metric-item">
              <div className="metric-number">{metrics.resolved}</div>
              <div className="metric-label">Resolved</div>
            </div>
          </div>
        </section>
      )}

      {/* Error State */}
      {error && (
        <section className="dashboard-section">
          <div className="error-box">
            <h3>⚠️ Error Loading Dashboard</h3>
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="button primary"
            >
              Retry
            </button>
          </div>
        </section>
      )}

      {/* Loading State */}
      {isLoading && (
        <section className="dashboard-section">
          <div className="loading-box">
            <div className="spinner"></div>
            <p>Loading complaints...</p>
          </div>
        </section>
      )}

      {/* Map Section */}
      {!isLoading && complaints.length > 0 && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2>Live Infrastructure Map</h2>
            <p>Geolocation view of all reported issues</p>
          </div>
          <div className="map-wrapper">
            <InfrastructureMap
              complaints={complaints}
              filters={undefined}
            />
          </div>
        </section>
      )}

      {/* Recent Issues Table */}
      {!isLoading && complaints.length > 0 && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2>Recent Reports</h2>
            <p>Latest infrastructure complaints</p>
          </div>
          <div className="issues-table">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {complaints.slice(0, 10).map(complaint => (
                  <tr key={complaint.id}>
                    <td className="title">{complaint.title}</td>
                    <td>
                      <span className={`priority-badge priority-${complaint.priorityLevel?.toLowerCase()}`}>
                        {complaint.priorityLevel}
                      </span>
                    </td>
                    <td>{complaint.status}</td>
                    <td className="location">{complaint.location || 'Not specified'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* No Data State */}
      {!isLoading && complaints.length === 0 && !error && (
        <section className="dashboard-section">
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>No Issues Yet</h3>
            <p>When infrastructure issues are reported, they'll appear here</p>
          </div>
        </section>
      )}
    </div>
  );
}

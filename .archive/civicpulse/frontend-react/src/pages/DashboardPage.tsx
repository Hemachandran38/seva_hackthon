import { useState, useMemo, useEffect } from 'react';
import { apiComplaintService } from '../services/apiComplaintService';
import { InfrastructureMap } from '../components/map/InfrastructureMap';
import '../styles/dashboard.css';
import type { Complaint } from '../types/complaint';

export function DashboardPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch complaints from API on mount
  useEffect(() => {
    const fetchComplaints = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiComplaintService.getAllComplaints();
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
  
  // Filter state
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Filter complaints based on current filters
  const filteredComplaints = useMemo(() => {
    return complaints.filter(complaint => {
      const priorityMatch = priorityFilter === 'all' || 
        complaint.priorityLevel === priorityFilter;
      
      const statusMatch = statusFilter === 'all' || 
        complaint.status === statusFilter;

      return priorityMatch && statusMatch;
    });
  }, [complaints, priorityFilter, statusFilter]);

  // Calculate metrics from ALL complaints (not filtered)
  const metrics = useMemo(() => {
    return {
      total: complaints.length,
      open: complaints.filter(c => c.status !== 'Resolved').length,
      high: complaints.filter(c => c.priorityLevel === 'High' || c.priorityLevel === 'Critical').length,
      resolved: complaints.filter(c => c.status === 'Resolved').length,
    };
  }, [complaints]);

  // Map priority level to color
  // (Kept for future use if needed for color coding)
  // const getPriorityColor = (priority: string): string => {
  //   switch (priority.toLowerCase()) {
  //     case 'critical':
  //       return '#e53e3e';
  //     case 'high':
  //       return '#e53e3e';
  //     case 'medium':
  //       return '#dd6b20';
  //     case 'low':
  //       return '#3182ce';
  //     default:
  //       return '#888';
  //   }
  // };

  return (
    <div className="dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-brand">
          <span className="brand-icon">⚡</span>
          <div>
            <h1 className="brand-title">CivicPulse AI</h1>
            <p className="brand-subtitle">
              Public Infrastructure Fault Monitoring &amp; Repair Prioritization
            </p>
          </div>
        </div>
        <div className="header-meta">
          <span className="badge badge-demo">📊 Live Dashboard</span>
          <span className="header-location">📍 Coimbatore, Tamil Nadu</span>
        </div>
      </header>

      {/* Error State */}
      {error && (
        <div style={{
          backgroundColor: '#fee2e2',
          color: '#991b1b',
          padding: '16px',
          margin: '16px',
          borderRadius: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>⚠️ {error}</span>
          <button
            onClick={() => window.location.reload()}
            style={{
              backgroundColor: '#991b1b',
              color: 'white',
              padding: '8px 16px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          backgroundColor: '#f3f4f6',
          margin: '16px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>⏳</div>
            <p>Loading complaints from backend...</p>
          </div>
        </div>
      )}

      {/* No Data State */}
      {!isLoading && complaints.length === 0 && !error && (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          backgroundColor: '#f3f4f6',
          margin: '16px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>📭</div>
            <p>No complaints yet. Start by reporting an issue!</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!isLoading && complaints.length > 0 && (
        <main className="dashboard-main">
        {/* Sidebar */}
        <aside className="dashboard-sidebar">
          {/* Metrics Panel */}
          <section className="panel metrics-panel">
            <h2 className="panel-title">Dashboard Overview</h2>
            <div className="metrics-grid">
              <div className="metric-card">
                <span className="metric-value">{metrics.total}</span>
                <span className="metric-label">Total Reports</span>
              </div>
              <div className="metric-card metric-open">
                <span className="metric-value">{metrics.open}</span>
                <span className="metric-label">Open Complaints</span>
              </div>
              <div className="metric-card metric-high">
                <span className="metric-value">{metrics.high}</span>
                <span className="metric-label">High Priority</span>
              </div>
              <div className="metric-card metric-resolved">
                <span className="metric-value">{metrics.resolved}</span>
                <span className="metric-label">Resolved</span>
              </div>
            </div>
          </section>

          {/* Filters */}
          <section className="panel filter-panel">
            <h2 className="panel-title">Filters</h2>

            <div className="filter-group">
              <label className="filter-label">Priority Level</label>
              <div className="filter-options">
                {['all', 'Critical', 'High', 'Medium', 'Low'].map(level => (
                  <label
                    key={level}
                    className={`filter-chip ${priorityFilter === level ? 'active' : ''}`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={level}
                      checked={priorityFilter === level}
                      onChange={(e) => setPriorityFilter(e.target.value)}
                    />
                    {level === 'all' ? 'All Levels' : level}
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label className="filter-label">Status</label>
              <div className="filter-options">
                {['all', 'Reported', 'Under Review', 'Assigned', 'In Progress', 'Awaiting Verification', 'Resolved'].map(
                  (status) => (
                    <label
                      key={status}
                      className={`filter-chip ${statusFilter === status ? 'active' : ''}`}
                    >
                      <input
                        type="radio"
                        name="status"
                        value={status}
                        checked={statusFilter === status}
                        onChange={(e) => setStatusFilter(e.target.value)}
                      />
                      {status === 'all' ? 'All Status' : status}
                    </label>
                  )
                )}
              </div>
            </div>

            <button
              className="btn-reset"
              onClick={() => {
                setPriorityFilter('all');
                setStatusFilter('all');
              }}
            >
              Reset Filters
            </button>
          </section>

          {/* Legend */}
          <section className="panel legend-panel">
            <h2 className="panel-title">Map Legend</h2>
            <ul className="legend-list">
              <li className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#991b1b' }}></span>
                <span>Critical Priority</span>
              </li>
              <li className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#e53e3e' }}></span>
                <span>High Priority</span>
              </li>
              <li className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#dd6b20' }}></span>
                <span>Medium Priority</span>
              </li>
              <li className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#3182ce' }}></span>
                <span>Low Priority</span>
              </li>
              <li className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#10b981' }}></span>
                <span>Resolved</span>
              </li>
            </ul>
            <p className="legend-note">
              Markers represent <strong>infrastructure complaints</strong> and their geolocations.
            </p>
          </section>

          {/* Visible count */}
          <section className="panel count-panel">
            <p className="visible-count">
              Showing <strong>{filteredComplaints.length}</strong> of{' '}
              <strong>{complaints.length}</strong> complaints
            </p>
          </section>
        </aside>

        {/* Map Container */}
        <div className="map-container">
          <InfrastructureMap
            complaints={filteredComplaints}
            filters={{
              priority:
                priorityFilter === 'all'
                  ? undefined
                  : [priorityFilter],
              status:
                statusFilter === 'all'
                  ? undefined
                  : [statusFilter],
            }}
          />
        </div>
        </main>
      )}

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>
          CivicPulse AI — Infrastructure Dashboard &nbsp;|&nbsp; Map tiles &copy;{' '}
          <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">
            OpenStreetMap
          </a>{' '}
          &nbsp;|&nbsp; All data is real-time from active reports.
        </p>
      </footer>
    </div>
  );
}


import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Complaint } from '../../types/complaint';
import './InfrastructureMap.css';

interface InfrastructureMapProps {
  complaints: Complaint[];
  selectedComplaintId?: string;
  filters?: {
    priority?: string[];
    status?: string[];
    category?: string[];
  };
}

// Create custom marker icons based on priority
function getMarkerIcon(priorityLevel: Complaint['priorityLevel'], status: Complaint['status']) {
  let color = '#3b82f6'; // Default blue
  
  if (status === 'Resolved') {
    color = '#10b981'; // Green
  } else if (priorityLevel === 'Critical') {
    color = '#991b1b'; // Dark red
  } else if (priorityLevel === 'High') {
    color = '#dc2626'; // Red
  } else if (priorityLevel === 'Medium') {
    color = '#f97316'; // Orange
  }

  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="2">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
    </svg>
  `;

  return L.divIcon({
    html: `<div class="map-marker" style="background-color: ${color};">${svgIcon}</div>`,
    className: 'custom-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40],
  });
}

export function InfrastructureMap({ complaints, selectedComplaintId, filters }: InfrastructureMapProps) {
  const [, setSelectedId] = useState<string | undefined>(selectedComplaintId);

  // Filter complaints with valid coordinates
  const filteredComplaints = useMemo(() => {
    return complaints.filter(complaint => {
      // Only show complaints with coordinates
      if (complaint.latitude === undefined || complaint.longitude === undefined) {
        return false;
      }

      // Apply filters if provided
      if (filters?.priority?.length && !filters.priority.includes(complaint.priorityLevel)) {
        return false;
      }
      if (filters?.status?.length && !filters.status.includes(complaint.status)) {
        return false;
      }
      if (filters?.category?.length && !filters.category.includes(complaint.category)) {
        return false;
      }

      return true;
    });
  }, [complaints, filters]);

  // Calculate center and bounds
  const defaultCenter: [number, number] = [22.3193, 73.1812]; // Coimbatore default
  const mapCenter = useMemo(() => {
    if (filteredComplaints.length === 0) {
      return defaultCenter;
    }

    const latitudes = filteredComplaints.map(c => c.latitude!);
    const longitudes = filteredComplaints.map(c => c.longitude!);

    const avgLat = latitudes.reduce((a, b) => a + b) / latitudes.length;
    const avgLng = longitudes.reduce((a, b) => a + b) / longitudes.length;

    return [avgLat, avgLng] as [number, number];
  }, [filteredComplaints]);

  if (filteredComplaints.length === 0) {
    return (
      <div className="map-empty">
        <div className="map-empty-content">
          <div className="map-empty-icon">📍</div>
          <h3>No geolocated complaints</h3>
          <p>Complaints appear here once they have latitude and longitude coordinates assigned.</p>
          <p className="map-empty-hint">Try submitting a report with location details, or adjust your filters.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="infrastructure-map-container">
      <MapContainer
        center={mapCenter}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        className="infrastructure-map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {filteredComplaints.map(complaint => (
          <Marker
            key={complaint.id}
            position={[complaint.latitude!, complaint.longitude!]}
            icon={getMarkerIcon(complaint.priorityLevel, complaint.status)}
            eventHandlers={{
              click: () => setSelectedId(complaint.id),
            }}
          >
            <Popup className="complaint-popup">
              <div className="popup-content">
                <div className="popup-header">
                  <div className="popup-id">{complaint.id}</div>
                  <div className={`popup-priority priority-${complaint.priorityLevel.toLowerCase()}`}>
                    {complaint.priorityLevel}
                  </div>
                </div>
                <h4>{complaint.title}</h4>
                <div className="popup-details">
                  <div>
                    <strong>Category:</strong> {complaint.category}
                  </div>
                  {complaint.assetId && (
                    <div>
                      <strong>Asset:</strong> {complaint.assetId}
                    </div>
                  )}
                  <div>
                    <strong>Status:</strong> {complaint.status}
                  </div>
                  <div>
                    <strong>Priority Score:</strong> {complaint.priorityScore}/100
                  </div>
                  {complaint.ward && (
                    <div>
                      <strong>Ward:</strong> {complaint.ward}
                    </div>
                  )}
                  <div>
                    <strong>Location:</strong> {complaint.location}
                  </div>
                  <div>
                    <strong>Reported:</strong>{' '}
                    {new Date(complaint.reportedAt).toLocaleDateString()}
                  </div>
                  {complaint.repeatComplaintCount > 0 && (
                    <div>
                      <strong>Repeat Reports:</strong> {complaint.repeatComplaintCount}
                    </div>
                  )}
                </div>
                <Link
                  to={`/track?id=${encodeURIComponent(complaint.id)}`}
                  className="button secondary small"
                >
                  View Details →
                </Link>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="map-stats">
        <div className="map-stat-item">
          <span className="stat-label">Geolocated Reports</span>
          <strong>{filteredComplaints.length}</strong>
        </div>
        <div className="map-stat-item">
          <span className="stat-label">Open Issues</span>
          <strong>
            {filteredComplaints.filter(c => c.status !== 'Resolved').length}
          </strong>
        </div>
        <div className="map-stat-item">
          <span className="stat-label">Critical/High</span>
          <strong>
            {filteredComplaints.filter(
              c => c.priorityLevel === 'Critical' || c.priorityLevel === 'High'
            ).length}
          </strong>
        </div>
      </div>

      <div className="map-legend">
        <div className="legend-title">Priority Levels</div>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#991b1b' }} />
            <span>Critical</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#dc2626' }} />
            <span>High</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#f97316' }} />
            <span>Medium</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#3b82f6' }} />
            <span>Low</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#10b981' }} />
            <span>Resolved</span>
          </div>
        </div>
      </div>
    </div>
  );
}

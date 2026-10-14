import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Trash2 } from 'lucide-react';
import './LocationSelector.css';

interface LocationSelectorProps {
  latitude?: number;
  longitude?: number;
  onLocationSelect: (lat: number, lng: number) => void;
  onLocationClear: () => void;
}

function MapClickHandler({ onLocationSelect }: { onLocationSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function LocationSelector({
  latitude,
  longitude,
  onLocationSelect,
  onLocationClear,
}: LocationSelectorProps) {
  const [mapOpen, setMapOpen] = useState(false);
  const defaultCenter: [number, number] = [22.3193, 73.1812]; // Coimbatore
  const mapCenter: [number, number] = latitude && longitude ? [latitude, longitude] : defaultCenter;

  const hasLocation = latitude !== undefined && longitude !== undefined;

  useEffect(() => {
    if (!mapOpen) {
      // Close any open popups or state when map is hidden
    }
  }, [mapOpen]);

  return (
    <div className="location-selector">
      <div className="location-display">
        {hasLocation ? (
          <div className="location-info">
            <div className="location-status">
              <MapPin size={16} />
              <strong>Location pinned</strong>
            </div>
            <div className="location-coords">
              Latitude: {latitude?.toFixed(6)} • Longitude: {longitude?.toFixed(6)}
            </div>
            <button
              type="button"
              className="button secondary small"
              onClick={() => {
                onLocationClear();
                setMapOpen(false);
              }}
            >
              <Trash2 size={14} /> Clear location
            </button>
          </div>
        ) : (
          <div className="location-empty">
            <MapPin size={20} />
            <div>
              <strong>No location selected</strong>
              <p>Click the map below or use the button to select a location.</p>
            </div>
          </div>
        )}
      </div>

      {!mapOpen ? (
        <button
          type="button"
          className="button secondary"
          onClick={() => setMapOpen(true)}
          style={{ marginTop: '12px' }}
        >
          <MapPin size={16} /> {hasLocation ? 'Adjust Location on Map' : 'Select Location on Map'}
        </button>
      ) : (
        <div className="map-selector-container">
          <MapContainer
            center={mapCenter}
            zoom={14}
            style={{ height: '300px', width: '100%', borderRadius: '6px' }}
            className="location-map"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />
            <MapClickHandler onLocationSelect={onLocationSelect} />
            {hasLocation && (
              <Marker
                position={[latitude, longitude]}
                icon={L.icon({
                  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41],
                })}
              />
            )}
          </MapContainer>
          <div className="map-help">
            <p>Click on the map to select your location, then close the map selector.</p>
          </div>
          <button
            type="button"
            className="button secondary"
            onClick={() => setMapOpen(false)}
            style={{ marginTop: '12px' }}
          >
            Done - Close Map
          </button>
        </div>
      )}

      <div className="location-note">
        <span>💡</span>
        <p>
          This demo stores coordinates in your browser only. Click anywhere on the map to select a location. You can always adjust it later.
        </p>
      </div>
    </div>
  );
}

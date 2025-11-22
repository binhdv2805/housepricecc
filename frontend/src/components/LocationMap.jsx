import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix cho default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

function LocationMarker({ position, setPosition, setLocationName }) {
  const [markerPosition, setMarkerPosition] = useState(position || [10.762622, 106.660172]); // Mặc định TP.HCM

  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setMarkerPosition([lat, lng]);
      setPosition([lat, lng]);
      
      // Reverse geocoding để lấy tên địa điểm
      fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
        .then(res => res.json())
        .then(data => {
          if (data.display_name) {
            setLocationName(data.display_name);
          }
        })
        .catch(err => console.error('Error fetching location name:', err));
    },
  });

  useEffect(() => {
    if (position) {
      setMarkerPosition(position);
    }
  }, [position]);

  return markerPosition ? <Marker position={markerPosition} /> : null;
}

export default function LocationMap({ position, onPositionChange, onLocationNameChange }) {
  const [mapPosition, setMapPosition] = useState(position || [10.762622, 106.660172]);

  const handlePositionChange = (newPosition) => {
    setMapPosition(newPosition);
    if (onPositionChange) {
      onPositionChange(newPosition);
    }
  };

  const handleLocationNameChange = (name) => {
    if (onLocationNameChange) {
      onLocationNameChange(name);
    }
  };

  return (
    <div style={{ width: '100%', height: '300px', borderRadius: '10px', overflow: 'hidden', border: '2px solid #e0e0e0' }}>
      <MapContainer
        center={mapPosition}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker
          position={mapPosition}
          setPosition={handlePositionChange}
          setLocationName={handleLocationNameChange}
        />
      </MapContainer>
    </div>
  );
}


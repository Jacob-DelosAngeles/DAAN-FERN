import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useAppStore } from '../store/useAppStore';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Map style configurations
const mapStyles = {
  OpenStreetMap: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors'
  },
  Satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri, Maxar, Earthstar Geographics'
  },
  '3D Terrain': {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri, HERE, Garmin, Intermap, increment P Corp.'
  },
  'Dark Mode': {
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '© OpenStreetMap contributors, © CartoDB'
  }
};

// Component to update map center when store changes
function MapUpdater() {
  const map = useMap();
  const { mapCenter, mapZoom } = useAppStore();
  
  useEffect(() => {
    map.setView(mapCenter, mapZoom);
  }, [map, mapCenter, mapZoom]);
  
  return null;
}

const MapView = () => {
  const { mapCenter, mapZoom, mapStyle, layerControls, vehicleData, potholeData, iriData } = useAppStore();
  const [mapKey, setMapKey] = useState(0);

  // Force map re-render when style changes
  useEffect(() => {
    setMapKey(prev => prev + 1);
  }, [mapStyle]);

  const currentStyle = mapStyles[mapStyle] || mapStyles.OpenStreetMap;

  return (
    <div className="w-full h-full relative">
      <MapContainer
        key={mapKey}
        center={mapCenter}
        zoom={mapZoom}
        className="w-full h-full"
        zoomControl={true}
        scrollWheelZoom={true}
        doubleClickZoom={true}
        dragging={true}
        touchZoom={true}
      >
        <MapUpdater />
        
        <TileLayer
          url={currentStyle.url}
          attribution={currentStyle.attribution}
        />
        
        
        {/* Vehicle markers */}
        {layerControls.vehicles && vehicleData && vehicleData.map((vehicle, index) => (
          <Marker 
            key={`vehicle-${index}`} 
            position={[vehicle.latitude, vehicle.longitude]}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-blue-600">Vehicle Detection</h4>
                <p className="text-sm">Type: {vehicle.type || 'Unknown'}</p>
                <p className="text-sm">Confidence: {vehicle.confidence || 'N/A'}</p>
                <p className="text-xs text-gray-500">
                  {new Date(vehicle.timestamp).toLocaleString()}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Pothole markers */}
        {layerControls.potholes && potholeData && potholeData.map((pothole, index) => (
          <Marker 
            key={`pothole-${index}`} 
            position={[pothole.latitude, pothole.longitude]}
            icon={L.icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            })}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-red-600">Pothole Detection</h4>
                <p className="text-sm">Severity: {pothole.severity || 'Unknown'}</p>
                <p className="text-sm">Size: {pothole.size || 'N/A'}</p>
                <p className="text-xs text-gray-500">
                  {new Date(pothole.timestamp).toLocaleString()}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* IRI data visualization */}
        {layerControls.iri && iriData && iriData.map((segment, index) => (
          <Marker 
            key={`iri-${index}`} 
            position={[segment.latitude, segment.longitude]}
            icon={L.icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            })}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-green-600">IRI Measurement</h4>
                <p className="text-sm">Value: {segment.iri_value?.toFixed(2) || 'N/A'}</p>
                <p className="text-sm">Quality: {segment.quality || 'Unknown'}</p>
                <p className="text-xs text-gray-500">
                  {new Date(segment.timestamp).toLocaleString()}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;

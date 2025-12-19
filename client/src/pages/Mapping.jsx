import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import { useDropzone } from 'react-dropzone';
import { fileService } from '../services/api';
import { Upload, Map as MapIcon, Truck, AlertTriangle, Layers } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet marker icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const Mapping = () => {
    const [activeTab, setActiveTab] = useState('vehicle');
    const [loading, setLoading] = useState(false);
    const [mapData, setMapData] = useState({ vehicles: [], potholes: [], pavement: [] });
    const [error, setError] = useState(null);

    const onDrop = async (acceptedFiles) => {
        setLoading(true);
        setError(null);

        try {
            // Upload files based on active tab
            const response = await fileService.uploadFile(acceptedFiles[0], activeTab); // Currently handling single file for simplicity, but backend supports multiple

            if (response.success) {
                setMapData(prev => ({
                    ...prev,
                    [activeTab === 'vehicle' ? 'vehicles' : activeTab === 'pothole' ? 'potholes' : 'pavement']: response.data
                }));
            } else {
                setError(response.message || 'Failed to process file');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during processing');
        } finally {
            setLoading(false);
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv']
        }
    });

    const tabs = [
        { id: 'vehicle', label: 'Vehicle Detection', icon: <Truck size={18} /> },
        { id: 'pothole', label: 'Pothole Detection', icon: <AlertTriangle size={18} /> },
        { id: 'pavement', label: 'Pavement Type', icon: <Layers size={18} /> },
    ];

    // Helper to get center of map
    const getCenter = () => {
        if (mapData.vehicles.length > 0) return [mapData.vehicles[0].lat, mapData.vehicles[0].lon];
        if (mapData.potholes.length > 0) return [mapData.potholes[0].lat, mapData.potholes[0].lon];
        if (mapData.pavement.length > 0 && mapData.pavement[0].points.length > 0) return mapData.pavement[0].points[0];
        return [14.1648, 121.2413]; // Default to UPLB coordinates
    };

    return (
        <div className="h-[calc(100vh-140px)] flex flex-col">
            <div className="bg-white rounded-lg shadow p-4 mb-4">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold flex items-center">
                        <MapIcon className="mr-2 text-blue-600" />
                        Mapping Visualization
                    </h2>
                    <div className="flex space-x-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center px-4 py-2 rounded-md transition-colors ${activeTab === tab.id
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                <span className="mr-2">{tab.icon}</span>
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
                        }`}
                >
                    <input {...getInputProps()} />
                    <div className="flex items-center justify-center text-gray-600">
                        <Upload className="mr-2" size={20} />
                        {loading ? 'Processing...' : `Upload ${tabs.find(t => t.id === activeTab).label} CSV Data`}
                    </div>
                </div>

                {error && (
                    <div className="mt-2 text-red-600 text-sm text-center">
                        {error}
                    </div>
                )}
            </div>

            <div className="flex-1 bg-white rounded-lg shadow overflow-hidden border border-gray-200">
                <MapContainer center={getCenter()} zoom={15} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />

                    {/* Vehicle Markers */}
                    {mapData.vehicles.map((vehicle, idx) => (
                        <Marker
                            key={`vehicle-${idx}`}
                            position={[vehicle.lat, vehicle.lon]}
                        >
                            <Popup>
                                <div dangerouslySetInnerHTML={{ __html: vehicle.popup_html }} />
                            </Popup>
                            <Tooltip>{vehicle.tooltip}</Tooltip>
                        </Marker>
                    ))}

                    {/* Pothole Markers */}
                    {mapData.potholes.map((pothole, idx) => (
                        <Marker
                            key={`pothole-${idx}`}
                            position={[pothole.lat, pothole.lon]}
                        >
                            <Popup>
                                <div dangerouslySetInnerHTML={{ __html: pothole.popup_html }} />
                            </Popup>
                            <Tooltip>{pothole.tooltip}</Tooltip>
                        </Marker>
                    ))}

                    {/* Pavement Segments */}
                    {mapData.pavement.map((segment, idx) => (
                        <Polyline
                            key={`pavement-${idx}`}
                            positions={segment.points}
                            color={segment.color}
                            weight={5}
                        >
                            <Tooltip sticky>Type: {segment.type}</Tooltip>
                        </Polyline>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
};

export default Mapping;

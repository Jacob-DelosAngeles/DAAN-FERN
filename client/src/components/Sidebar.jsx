import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, AlertCircle, CheckCircle, Map as MapIcon, Car, AlertTriangle, Activity, Layers, Trash } from 'lucide-react';
import { fileService } from '../services/api';
import useAppStore from '../store/useAppStore';
// ... (imports)



const StreamlitHeader = ({ title, icon: Icon }) => (
  <div className="bg-[#262730] text-white p-3 rounded-md flex items-center justify-center mb-2 shadow-sm">
    {Icon && <Icon size={18} className="mr-2" />}
    <span className="font-semibold text-sm">{title}</span>
  </div>
);

const UploadSection = ({ title, subLabel, onUpload, icon, accept = { 'text/csv': ['.csv'] } }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [fileName, setFileName] = useState('');

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    setLoading(true);
    setError(null);
    setSuccess(false);
    setFileName(acceptedFiles[0].name);

    try {
      await onUpload(acceptedFiles[0]);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles: 1
  });

  return (
    <div className="mb-6">
      <StreamlitHeader title={title} icon={icon} />

      <div className="px-1">
        <p className="text-xs text-gray-600 mb-2 font-medium">{subLabel}</p>

        <div
          {...getRootProps()}
          className={`bg-white border border-gray-300 rounded p-4 flex items-center justify-between cursor-pointer hover:border-red-400 transition-colors ${isDragActive ? 'border-red-500 bg-red-50' : ''
            }`}
        >
          <input {...getInputProps()} />
          <div className="flex items-center text-gray-500">
            <Upload size={16} className="mr-2" />
            <span className="text-xs">Drag and drop files here</span>
          </div>
          <button className="bg-white border border-gray-300 text-xs px-3 py-1 rounded hover:bg-gray-50 transition-colors">
            Browse files
          </button>
        </div>
        <p className="text-[10px] text-gray-400 mt-1">Limit 200MB per file • CSV</p>

        {loading && <p className="mt-2 text-xs text-blue-600 font-medium animate-pulse">Processing...</p>}

        {error && (
          <div className="mt-2 flex items-start text-xs text-red-600 bg-red-50 p-2 rounded border border-red-100">
            <AlertCircle size={14} className="mr-1 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mt-2 flex items-center text-xs text-green-700 bg-green-50 p-2 rounded border border-green-100">
            <CheckCircle size={14} className="mr-1 flex-shrink-0" />
            <span className="truncate">Uploaded: {fileName}</span>
          </div>
        )}
      </div>
    </div>
  );
};

const PotholeUploadSection = ({ title, onUpload, icon }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [imageFiles, setImageFiles] = useState([]);

  const handleCsvDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) setCsvFile(acceptedFiles[0]);
  };

  const handleImagesDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) setImageFiles(prev => [...prev, ...acceptedFiles]);
  };

  const { getRootProps: getCsvRoot, getInputProps: getCsvInput } = useDropzone({
    onDrop: handleCsvDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1
  });

  const { getRootProps: getImagesRoot, getInputProps: getImagesInput } = useDropzone({
    onDrop: handleImagesDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
    multiple: true
  });

  const handleUpload = async () => {
    if (!csvFile) { // Images are optional generally, but user asked for both. Let's make CSV required at least.
      setError('CSV file is required');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Bundle CSV first, then images
      const filesToUpload = [csvFile, ...imageFiles];
      await onUpload(filesToUpload);

      setSuccess(true);
      setCsvFile(null);
      setImageFiles([]);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-6">
      <StreamlitHeader title={title} icon={icon} />

      <div className="px-1 space-y-3">
        {/* CSV Input */}
        <div>
          <p className="text-xs text-gray-600 mb-1 font-medium">1. Pothole Data CSV (Required)</p>
          <div {...getCsvRoot()} className="bg-white border border-gray-300 rounded p-3 flex items-center justify-between cursor-pointer hover:border-blue-400">
            <input {...getCsvInput()} />
            <div className="flex items-center text-gray-500 truncate">
              <Upload size={14} className="mr-2 flex-shrink-0" />
              <span className="text-xs truncate">{csvFile ? csvFile.name : 'Drag CSV here'}</span>
            </div>
          </div>
        </div>

        {/* Images Input */}
        <div>
          <p className="text-xs text-gray-600 mb-1 font-medium">2. Pothole Images (Optional)</p>
          <div {...getImagesRoot()} className="bg-white border border-gray-300 rounded p-3 flex items-center justify-between cursor-pointer hover:border-blue-400">
            <input {...getImagesInput()} />
            <div className="flex items-center text-gray-500 truncate">
              <Upload size={14} className="mr-2 flex-shrink-0" />
              <span className="text-xs truncate">{imageFiles.length > 0 ? `${imageFiles.length} images selected` : 'Drag images here'}</span>
            </div>
          </div>
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={loading || !csvFile}
          className={`w-full py-2 rounded text-xs font-semibold text-white transition-colors ${loading || !csvFile ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
        >
          {loading ? 'Uploading...' : 'Upload Batch'}
        </button>

        {error && (
          <div className="mt-2 flex items-start text-xs text-red-600 bg-red-50 p-2 rounded border border-red-100">
            <AlertCircle size={14} className="mr-1 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mt-2 flex items-center text-xs text-green-700 bg-green-50 p-2 rounded border border-green-100">
            <CheckCircle size={14} className="mr-1 flex-shrink-0" />
            <span>Upload successful!</span>
          </div>
        )}
      </div>
    </div>
  );
};

const LayerToggle = ({ label, active, onToggle, color }) => (
  <div className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0">
    <div className="flex items-center">
      <span className={`w-3 h-3 rounded-full mr-2 ${color}`}></span>
      <span className="text-sm text-gray-700">{label}</span>
    </div>
    <label className="relative inline-flex items-center cursor-pointer">
      <input type="checkbox" checked={active} onChange={onToggle} className="sr-only peer" />
      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#ff4b4b]"></div>
    </label>
  </div>
);

const Sidebar = () => {
  const {
    setVehicles, setPotholes, setPavement,
    iriFiles, setIriFiles, addIriFile, toggleIriFile, removeIriFile, clearIriFiles,
    potholeFiles, setPotholeFiles, addPotholeFile, togglePotholeFile, removePotholeFile, clearPotholeFiles,
    vehicleFiles, setVehicleFiles, addVehicleFile, toggleVehicleFile, removeVehicleFile, clearVehicleFiles,
    pavementFiles, setPavementFiles, addPavementFile, togglePavementFile, removePavementFile, clearPavementFiles,
    activeLayers, toggleLayer
  } = useAppStore();

  const [deleteConfirm, setDeleteConfirm] = useState(null); // ID of file pending deletion confirmation
  const [isRestoring, setIsRestoring] = useState(true); // Track initial data loading
  const [restoreError, setRestoreError] = useState(null); // Track loading errors

  // Sync Pothole Files to Map Layer
  useEffect(() => {
    const activeMarkers = potholeFiles
      .filter(f => f.visible)
      .flatMap(f => f.data || []);
    setPotholes(activeMarkers);
  }, [potholeFiles, setPotholes]);

  // Sync Vehicle Files to Map Layer
  useEffect(() => {
    const activeMarkers = vehicleFiles
      .filter(f => f.visible)
      .flatMap(f => f.data || []);
    setVehicles(activeMarkers);
  }, [vehicleFiles, setVehicles]);

  // Sync Pavement Files to Map Layer
  useEffect(() => {
    const activeSegments = pavementFiles
      .filter(f => f.visible)
      .flatMap(f => f.data || []);
    setPavement(activeSegments);
  }, [pavementFiles, setPavement]);

  // Persistence: Restore files on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // 1. Restore IRI Files
        const iriRes = await fileService.getUploadedFiles('iri');
        if (iriRes.success && iriRes.files) {
          const uniqueFiles = {};
          iriRes.files.forEach(f => { uniqueFiles[f.original_filename] = f; });
          const filesToRestore = Object.values(uniqueFiles);

          const restoredIriFiles = [];
          for (const file of filesToRestore) {
            try {
              const computeRes = await fileService.computeIRI(file.filename);
              if (computeRes.success) {
                restoredIriFiles.push({
                  id: file.id,
                  filename: file.original_filename,
                  segments: computeRes.segments,
                  raw_data: computeRes.raw_data,
                  filtered_data: computeRes.filtered_data,
                  visible: true,
                  stats: {
                    averageIri: computeRes.segments.reduce((acc, seg) => acc + seg.iri_value, 0) / computeRes.segments.length,
                    maxIri: Math.max(...computeRes.segments.map(s => s.iri_value)),
                    avgSpeed: computeRes.segments.reduce((acc, seg) => acc + seg.mean_speed, 0) / computeRes.segments.length,
                    totalDistance: computeRes.segments[computeRes.segments.length - 1].distance_end,
                    totalSegments: computeRes.total_segments
                  }
                });
              }
            } catch (e) { console.error("Restore IRI Error", e); }
          }
          if (restoredIriFiles.length > 0) setIriFiles(restoredIriFiles);
        }

        // 2. Restore Pothole Data
        const potholeRes = await fileService.getUploadedFiles('pothole');
        if (potholeRes.success && potholeRes.files) {
          const csvFiles = potholeRes.files.filter(f => f.filename.endsWith('.csv'));
          const uniquePotholes = {};
          csvFiles.forEach(f => { uniquePotholes[f.original_filename] = f; });

          const restoredPotholeFiles = [];
          for (const file of Object.values(uniquePotholes)) {
            try {
              const processRes = await fileService.processPotholes(file.filename);
              if (processRes.success) {
                restoredPotholeFiles.push({
                  id: file.id,
                  filename: file.original_filename,
                  data: processRes.data,
                  visible: true
                });
              }
            } catch (e) { console.error("Restore Pothole Error", e); }
          }
          if (restoredPotholeFiles.length > 0) setPotholeFiles(restoredPotholeFiles);
        }

        // 3. Restore Vehicle Data
        const vehicleRes = await fileService.getUploadedFiles('vehicle');
        if (vehicleRes.success && vehicleRes.files) {
          const uniqueVehicles = {};
          vehicleRes.files.forEach(f => { uniqueVehicles[f.original_filename] = f; });

          const restoredVehicleFiles = [];
          for (const file of Object.values(uniqueVehicles)) {
            try {
              const processRes = await fileService.processVehicles(file.filename);
              if (processRes.success) {
                restoredVehicleFiles.push({
                  id: file.id,
                  filename: file.original_filename,
                  data: processRes.data,
                  visible: true
                });
              }
            } catch (e) { console.error("Restore Vehicle Error", e); }
          }
          if (restoredVehicleFiles.length > 0) setVehicleFiles(restoredVehicleFiles);
        }

        // 4. Restore Pavement Data
        const pavementRes = await fileService.getUploadedFiles('pavement');
        if (pavementRes.success && pavementRes.files) {
          const uniquePavement = {};
          pavementRes.files.forEach(f => { uniquePavement[f.original_filename] = f; });

          const restoredPavementFiles = [];
          for (const file of Object.values(uniquePavement)) {
            try {
              const processRes = await fileService.processPavement(file.filename);
              if (processRes.success) {
                restoredPavementFiles.push({
                  id: file.id,
                  filename: file.original_filename,
                  data: processRes.data,
                  visible: true
                });
              }
            } catch (e) { console.error("Restore Pavement Error", e); }
          }
          if (restoredPavementFiles.length > 0) setPavementFiles(restoredPavementFiles);
        }

      } catch (err) {
        console.error("Failed to restore session:", err);
        setRestoreError('Failed to load data. Server may be starting up. Please try again.');
      } finally {
        setIsRestoring(false);
      }
    };

    restoreSession();
  }, []);

  // Retry loading data
  const handleRetryLoad = () => {
    setIsRestoring(true);
    setRestoreError(null);
    // Trigger page reload to restart the restore process
    window.location.reload();
  };

  const handleDeleteIri = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await fileService.deleteFile(id);
      if (res.success) {
        removeIriFile(id);
        setDeleteConfirm(null);
      } else {
        alert(res.message || 'Delete failed');
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleDeletePothole = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await fileService.deleteFile(id);
      if (res.success) {
        removePotholeFile(id);
        setDeleteConfirm(null);
      } else {
        alert(res.message || 'Delete failed');
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleDeleteVehicle = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await fileService.deleteFile(id);
      if (res.success) {
        removeVehicleFile(id);
        setDeleteConfirm(null);
      } else {
        alert(res.message || 'Delete failed');
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleDeletePavement = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await fileService.deleteFile(id);
      if (res.success) {
        removePavementFile(id);
        setDeleteConfirm(null);
      } else {
        alert(res.message || 'Delete failed');
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleIriUpload = async (file) => {
    const uploadRes = await fileService.uploadFile(file, 'iri');
    if (uploadRes.success) {
      // fileService returns the object directly for single files (no data prop), or {data: [...]} for arrays
      const result = uploadRes.data ? ((Array.isArray(uploadRes.data)) ? uploadRes.data[0] : uploadRes.data) : uploadRes;

      if (!result || !result.filename) throw new Error("Invalid response format from server");

      const filename = result.filename;

      const computeRes = await fileService.computeIRI(filename);
      if (computeRes.success) {
        addIriFile({
          id: result.id, // Use real DB ID
          filename: file.name,
          segments: computeRes.segments,
          raw_data: computeRes.raw_data,
          filtered_data: computeRes.filtered_data,
          stats: {
            averageIri: computeRes.segments.reduce((acc, seg) => acc + seg.iri_value, 0) / computeRes.segments.length,
            maxIri: Math.max(...computeRes.segments.map(s => s.iri_value)),
            avgSpeed: computeRes.segments.reduce((acc, seg) => acc + seg.mean_speed, 0) / computeRes.segments.length,
            totalDistance: computeRes.segments[computeRes.segments.length - 1].distance_end,
            totalSegments: computeRes.total_segments
          }
        });
      } else {
        throw new Error(computeRes.message);
      }
    } else {
      throw new Error(uploadRes.message);
    }
  };

  const handleVehicleUpload = async (file) => {
    const res = await fileService.uploadFile(file, 'vehicle');
    if (res.success) {
      const result = res.data ? ((Array.isArray(res.data)) ? res.data[0] : res.data) : res;
      if (!result || !result.filename) throw new Error("Invalid response format from server");

      const processRes = await fileService.processVehicles(result.filename);
      if (processRes.success) {
        addVehicleFile({
          id: result.id, // Use real DB ID
          filename: file.name,
          data: processRes.data,
          visible: true
        });
      }
    } else throw new Error(res.message);
  };


  // Updated to handle array of files
  const handlePotholeUpload = async (files) => {
    // files is now an array: [csv, ...images]
    const uploadRes = await fileService.uploadFile(files, 'pothole');

    if (uploadRes.success) {
      // Get the CSV result
      const results = uploadRes.data || (Array.isArray(uploadRes) ? uploadRes : [uploadRes]);
      const csvResult = results.find(r => r.filename.toLowerCase().endsWith('.csv') && r.success);

      if (csvResult) {
        const processRes = await fileService.processPotholes(csvResult.filename);
        if (processRes.success) {
          addPotholeFile({
            id: csvResult.id || Date.now(),
            filename: csvResult.original_filename || csvResult.filename,
            data: processRes.data,
            visible: true
          });
        } else {
          throw new Error(processRes.message);
        }
      } else {
        // Try to find specific failure message
        const failedCsv = results.find(r => r.filename.toLowerCase().endsWith('.csv'));
        if (failedCsv) {
          throw new Error(failedCsv.message || "CSV upload failed");
        }
        throw new Error("CSV upload failed or not found in response");
      }
    } else {
      throw new Error(uploadRes.message);
    }
  };

  const handlePavementUpload = async (file) => {
    const res = await fileService.uploadFile(file, 'pavement');
    if (res.success) {
      const result = res.data ? ((Array.isArray(res.data)) ? res.data[0] : res.data) : res;
      if (!result || !result.filename) throw new Error("Invalid response format from server");

      const processRes = await fileService.processPavement(result.filename);
      if (processRes.success) {
        addPavementFile({
          id: result.id, // Use real DB ID
          filename: file.name,
          data: processRes.data,
          visible: true
        });
      }
    } else throw new Error(res.message);
  };

  return (
    <div className="w-96 bg-blue-50 border-r border-gray-200 h-full overflow-y-auto flex-shrink-0 shadow-sm z-0 custom-scrollbar">
      <div className="p-6">
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#262730] mb-1">Project DAAN Express</h2>
          <div className="h-0.5 w-full bg-blue-500 mb-2 opacity-50"></div>
          <p className="text-xs text-gray-500 italic">Digital Analytics for Asset-based Navigation of Roads</p>
        </div>

        {/* Loading Indicator */}
        {isRestoring && (
          <div className="mb-6 bg-blue-100 border border-blue-300 rounded-lg p-4 text-center">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full mb-2"></div>
            <p className="text-sm font-medium text-blue-800">Loading your data...</p>
            <p className="text-xs text-blue-600 mt-1">This may take a moment on first load</p>
          </div>
        )}

        {/* Error with Retry */}
        {!isRestoring && restoreError && (
          <div className="mb-6 bg-amber-100 border border-amber-300 rounded-lg p-4 text-center">
            <p className="text-sm font-medium text-amber-800">⚠️ {restoreError}</p>
            <button
              onClick={handleRetryLoad}
              className="mt-3 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold px-4 py-2 rounded transition-colors"
            >
              Retry Loading
            </button>
          </div>
        )}

        <UploadSection
          title="Vehicle Detection Data"
          subLabel="Upload Vehicle Detection CSV Files"
          icon={Car}
          onUpload={handleVehicleUpload}
        />

        {/* Replaced generic section with PotholeUploadSection */}
        <PotholeUploadSection
          title="Pothole Detection Data"
          icon={AlertTriangle}
          onUpload={handlePotholeUpload}
        />

        <UploadSection
          title="IRI Sensor Data"
          subLabel="Upload IRI Sensor CSV Files"
          icon={Activity}
          onUpload={handleIriUpload}
        />

        <UploadSection
          title="Road Type Classification"
          subLabel="Upload Road Type CSV Files"
          icon={MapIcon}
          onUpload={handlePavementUpload}
        />

        <div className="mt-8">
          <StreamlitHeader title="Data Layers" icon={Layers} />
          <div className="bg-white p-3 rounded border border-gray-200">
            <LayerToggle
              label="Vehicles"
              active={activeLayers.vehicles}
              onToggle={() => toggleLayer('vehicles')}
              color="bg-blue-500"
            />
            {/* Individual Vehicle Files */}
            {activeLayers.vehicles && vehicleFiles.length > 0 && (
              <div className="mt-2 space-y-2 mb-4">
                {vehicleFiles.map(file => (
                  <div key={file.id} className="ml-4 pl-2 border-l-2 border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center min-w-0">
                        <input
                          type="checkbox"
                          checked={file.visible}
                          onChange={() => toggleVehicleFile(file.id)}
                          className="h-3 w-3 text-blue-600 rounded focus:ring-blue-500 mr-2"
                        />
                        <span className="text-xs font-medium text-gray-700 truncate w-24" title={file.filename}>
                          {file.filename}
                        </span>
                      </div>
                      {deleteConfirm === file.id ? (
                        <button
                          onClick={(e) => handleDeleteVehicle(file.id, e)}
                          className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded hover:bg-red-600 transition-colors"
                        >
                          Confirm
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm(file.id); setTimeout(() => setDeleteConfirm(null), 3000); }}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          title="Delete file"
                        >
                          <Trash size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <LayerToggle
              label="Potholes"
              active={activeLayers.potholes}
              onToggle={() => toggleLayer('potholes')}
              color="bg-red-500"
            />

            {/* Individual Pothole Files */}
            {activeLayers.potholes && potholeFiles.length > 0 && (
              <div className="mt-2 space-y-2 mb-4">
                {potholeFiles.map(file => (
                  <div key={file.id} className="ml-4 pl-2 border-l-2 border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center min-w-0">
                        <input
                          type="checkbox"
                          checked={file.visible}
                          onChange={() => togglePotholeFile(file.id)}
                          className="h-3 w-3 text-blue-600 rounded focus:ring-blue-500 mr-2"
                        />
                        <span className="text-xs font-medium text-gray-700 truncate w-24" title={file.filename}>
                          {file.filename}
                        </span>
                      </div>
                      {deleteConfirm === file.id ? (
                        <button
                          onClick={(e) => handleDeletePothole(file.id, e)}
                          className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded hover:bg-red-600 transition-colors"
                        >
                          Confirm
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm(file.id); setTimeout(() => setDeleteConfirm(null), 3000); }}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          title="Delete file"
                        >
                          <Trash size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <LayerToggle
              label="Pavement"
              active={activeLayers.pavement}
              onToggle={() => toggleLayer('pavement')}
              color="bg-gray-500"
            />

            {/* Individual Pavement Files */}
            {activeLayers.pavement && pavementFiles.length > 0 && (
              <div className="mt-2 space-y-2 mb-4">
                {pavementFiles.map(file => (
                  <div key={file.id} className="ml-4 pl-2 border-l-2 border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center min-w-0">
                        <input
                          type="checkbox"
                          checked={file.visible}
                          onChange={() => togglePavementFile(file.id)}
                          className="h-3 w-3 text-blue-600 rounded focus:ring-blue-500 mr-2"
                        />
                        <span className="text-xs font-medium text-gray-700 truncate w-24" title={file.filename}>
                          {file.filename}
                        </span>
                      </div>
                      {deleteConfirm === file.id ? (
                        <button
                          onClick={(e) => handleDeletePavement(file.id, e)}
                          className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded hover:bg-red-600 transition-colors"
                        >
                          Confirm
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm(file.id); setTimeout(() => setDeleteConfirm(null), 3000); }}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          title="Delete file"
                        >
                          <Trash size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <LayerToggle
              label="IRI Segments"
              active={activeLayers.iri}
              onToggle={() => toggleLayer('iri')}
              color="bg-green-500"
            />

            {/* Individual IRI Files */}
            {activeLayers.iri && iriFiles.length > 0 && (
              <div className="mt-2 space-y-2">
                {iriFiles.map(file => (
                  <div key={file.id} className="ml-4 pl-2 border-l-2 border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center min-w-0">
                        <input
                          type="checkbox"
                          checked={file.visible}
                          onChange={() => toggleIriFile(file.id)}
                          className="h-3 w-3 text-blue-600 rounded focus:ring-blue-500 mr-2"
                        />
                        <span className="text-xs font-medium text-gray-700 truncate w-24" title={file.filename}>
                          {file.filename}
                        </span>
                      </div>
                      {deleteConfirm === file.id ? (
                        <button
                          onClick={(e) => handleDeleteIri(file.id, e)}
                          className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded hover:bg-red-600 transition-colors"
                        >
                          Confirm
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm(file.id); setTimeout(() => setDeleteConfirm(null), 3000); }}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          title="Delete file"
                        >
                          <Trash size={12} />
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-1 text-[10px] text-gray-500">
                      <div>Avg IRI: <span className="font-semibold">{file.stats.averageIri.toFixed(2)}</span></div>
                      <div>Max IRI: <span className="font-semibold">{file.stats.maxIri.toFixed(2)}</span></div>
                      <div>Dist: <span className="font-semibold">{(file.stats.totalDistance / 1000).toFixed(2)}km</span></div>
                      <div>Speed: <span className="font-semibold">{file.stats.avgSpeed.toFixed(1)}m/s</span></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

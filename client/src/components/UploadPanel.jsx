import React, { useCallback, useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import apiService from '../services/apiService';

const UploadPanel = () => {
  const {
    uploadedFiles,
    isUploading,
    uploadProgress,
    setUploadedFiles,
    setIsUploading,
    setUploadProgress,
    setIriData,
    setIriResults,
    setIriComputationError
  } = useAppStore();

  const [uploadStatus, setUploadStatus] = useState({});
  const [error, setError] = useState(null);

  // Pothole-specific state
  const [potholeImages, setPotholeImages] = useState([]);
  const [potholeCsv, setPotholeCsv] = useState(null);

  useEffect(() => {
    setUploadedFiles([]);
    setIriData(null);
    setIriResults(null);
    setIriComputationError(null);
  }, []);

  const loadUploadedFiles = async () => {
    try {
      const response = await apiService.getUploadedFiles();
      setUploadedFiles(response.files || []);
    } catch (err) {
      console.error('Failed to load uploaded files:', err);
      setUploadedFiles([]);
    }
  };

  const handleFileUpload = useCallback(async (files, fileType) => {
    if (files.length === 0) return;

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const uploadPromises = files.map(async (file, index) => {
        try {
          setUploadStatus(prev => ({ ...prev, [file.name]: 'uploading' }));

          const typeMap = {
            'vehicles': 'vehicle',
            'potholes': 'pothole',
            'iri': 'iri',
            'images': 'pothole'
          };

          const backendType = typeMap[fileType] || 'iri';
          const response = await apiService.uploadFile(file, backendType);

          setUploadStatus(prev => ({ ...prev, [file.name]: 'success' }));
          setUploadProgress(((index + 1) / files.length) * 100);

          return { file, response, type: fileType };
        } catch (err) {
          setUploadStatus(prev => ({ ...prev, [file.name]: 'error' }));
          throw err;
        }
      });

      const results = await Promise.all(uploadPromises);

      await loadUploadedFiles();

      const iriFiles = results.filter(r => r.type === 'iri');
      if (iriFiles.length > 0) {
        await computeIRIForFiles(iriFiles);
      }

    } catch (err) {
      setError(err.message);
      console.error('Upload failed:', err);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const handlePotholeUpload = useCallback(async () => {
    if (!potholeCsv || potholeImages.length === 0) {
      setError('Both CSV file and images are required for pothole upload');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    const BATCH_SIZE = 30; // Upload 30 images at a time to prevent timeout
    const totalFiles = potholeImages.length + 1; // +1 for CSV
    let uploadedCount = 0;

    try {
      // Step 1: Upload CSV first (must be processed first to get upload ID for linking)
      setUploadStatus(prev => ({ ...prev, [potholeCsv.name]: 'uploading' }));

      const csvResponse = await apiService.uploadFile([potholeCsv], 'pothole');

      setUploadStatus(prev => ({ ...prev, [potholeCsv.name]: 'success' }));
      uploadedCount++;
      setUploadProgress((uploadedCount / totalFiles) * 100);

      // Step 2: Upload images in batches
      const batches = [];
      for (let i = 0; i < potholeImages.length; i += BATCH_SIZE) {
        batches.push(potholeImages.slice(i, i + BATCH_SIZE));
      }

      for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
        const batch = batches[batchIndex];

        // Mark batch as uploading
        batch.forEach(img => {
          setUploadStatus(prev => ({ ...prev, [img.name]: 'uploading' }));
        });

        try {
          // Upload this batch
          setUploadStatus(prev => ({
            ...prev,
            '_batch_status': `Uploading batch ${batchIndex + 1} of ${batches.length}...`
          }));

          await apiService.uploadFile(batch, 'pothole');

          // Mark batch as success
          batch.forEach(img => {
            setUploadStatus(prev => ({ ...prev, [img.name]: 'success' }));
          });

          uploadedCount += batch.length;
          setUploadProgress((uploadedCount / totalFiles) * 100);

        } catch (batchErr) {
          // Mark this batch as error but continue with next batch
          batch.forEach(img => {
            setUploadStatus(prev => ({ ...prev, [img.name]: 'error' }));
          });
          console.error(`Batch ${batchIndex + 1} failed:`, batchErr);
          // Continue to next batch instead of failing entirely
        }
      }

      // Clear batch status
      setUploadStatus(prev => {
        const { _batch_status, ...rest } = prev;
        return rest;
      });

      // Clear selections
      setPotholeCsv(null);
      setPotholeImages([]);

      await loadUploadedFiles();

    } catch (err) {
      setError(err.message);
      setUploadStatus(prev => ({ ...prev, 'upload': 'error' }));
      console.error('Pothole upload failed:', err);
    } finally {
      setIsUploading(false);
    }
  }, [potholeCsv, potholeImages]);

  const computeIRIForFiles = useCallback(async (iriFiles) => {
    try {
      for (const { response } of iriFiles) {
        if (response.success) {
          const iriResults = await apiService.computeIRI(response.filename, {
            segmentLength: 100,
            cutoffFreq: 10.0
          });

          if (iriResults.success) {
            const mapData = iriResults.segments.map(segment => ({
              latitude: 14.1667 + (Math.random() - 0.5) * 0.01,
              longitude: 121.2500 + (Math.random() - 0.5) * 0.01,
              iri_value: segment.iri_value,
              timestamp: new Date().toISOString(),
              quality: segment.iri_value < 2 ? 'Good' : segment.iri_value < 4 ? 'Fair' : 'Poor'
            }));

            setIriData(mapData);
            setIriResults(iriResults);
          }
        }
      }
    } catch (err) {
      console.error('IRI computation failed:', err);
    }
  }, []);

  const handleFileSelect = useCallback((e, fileType) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileUpload(files, fileType);
    }
    e.target.value = '';
  }, [handleFileUpload]);

  const SimpleUploadArea = ({ title, description, icon, fileType, accept }) => {
    return (
      <div className="upload-area border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors">
        <div className="flex flex-col items-center">
          <div className="text-4xl mb-2">{icon}</div>
          <h3 className="font-semibold text-gray-700 mb-1">{title}</h3>
          <p className="text-sm text-gray-500 text-center mb-4">{description}</p>

          <label className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer inline-block">
            Browse Files
            <input
              type="file"
              accept={accept}
              multiple
              onChange={(e) => handleFileSelect(e, fileType)}
              className="hidden"
            />
          </label>
        </div>
      </div>
    );
  };

  return (
    <div className="p-4 space-y-6">
      {/* Vehicle Data Upload */}
      <div>
        <h3 className="section-header">
          🚗 Vehicle Detection Data
        </h3>
        <SimpleUploadArea
          title="Upload Vehicle Data CSV"
          description="CSV files with vehicle detection data including GPS coordinates, timestamps, and vehicle types"
          icon="🚗"
          fileType="vehicles"
          accept=".csv"
        />
      </div>

      {/* Pothole Data Upload - REDESIGNED */}
      <div>
        <h3 className="section-header">
          🚧 Pothole Detection Data
        </h3>
        <div className="space-y-4">
          {/* Images Upload */}
          <div className="upload-area border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="flex flex-col items-center">
              <div className="text-3xl mb-2">📸</div>
              <h4 className="font-semibold text-gray-700 mb-1">Pothole Images</h4>
              <p className="text-sm text-gray-500 mb-3">Select multiple images from your pothole detection folder</p>

              <label className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer inline-block">
                Browse Images
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.gif,.bmp"
                  multiple
                  onChange={(e) => setPotholeImages(Array.from(e.target.files))}
                  className="hidden"
                />
              </label>

              {potholeImages.length > 0 && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ {potholeImages.length} images selected
                </p>
              )}
            </div>
          </div>

          {/* CSV Upload */}
          <div className="upload-area border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="flex flex-col items-center">
              <div className="text-3xl mb-2">📄</div>
              <h4 className="font-semibold text-gray-700 mb-1">Pothole Data CSV</h4>
              <p className="text-sm text-gray-500 mb-3">CSV file containing pothole detection metadata</p>

              <label className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer inline-block">
                Browse CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setPotholeCsv(e.target.files[0])}
                  className="hidden"
                />
              </label>

              {potholeCsv && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ {potholeCsv.name}
                </p>
              )}
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handlePotholeUpload}
            disabled={!potholeCsv || potholeImages.length === 0 || isUploading}
            className={`w-full py-3 rounded-lg font-semibold transition-colors ${potholeCsv && potholeImages.length > 0 && !isUploading
              ? 'bg-green-500 hover:bg-green-600 text-white cursor-pointer'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
          >
            {isUploading ? 'Uploading...' : 'Upload Pothole Data'}
          </button>
        </div>
      </div>

      {/* IRI Data Upload */}
      <div>
        <h3 className="section-header">
          📏 IRI Sensor Data
        </h3>
        <SimpleUploadArea
          title="Upload IRI Data CSV"
          description="CSV files with IRI (International Roughness Index) sensor data"
          icon="📏"
          fileType="iri"
          accept=".csv"
        />
      </div>

      {/* Upload Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-700 mb-3">📊 Upload Summary</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Files:</span>
            <span className="font-medium">{uploadedFiles.length}</span>
          </div>
          {isUploading && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>{uploadStatus._batch_status || 'Uploading...'}</span>
                <span>{uploadProgress.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-semibold text-red-800 mb-2">❌ Upload Error</h4>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Upload Status */}
      {Object.keys(uploadStatus).length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">📤 Upload Status</h4>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {Object.entries(uploadStatus).map(([filename, status]) => (
              <div key={filename} className="flex items-center justify-between text-sm">
                <span className="text-blue-700 truncate">{filename}</span>
                <span className={`px-2 py-1 rounded text-xs ${status === 'success' ? 'bg-green-100 text-green-800' :
                  status === 'error' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                  {status === 'success' ? '✓ Success' :
                    status === 'error' ? '✗ Error' :
                      '⏳ Uploading'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPanel;

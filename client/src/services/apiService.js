const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  // Helper to get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // File Upload - supports single or multiple files
  async uploadFile(file, type = 'iri') {
    const formData = new FormData();

    // Backend expects 'files' (plural) as an array
    // Even for single file, we send it as an array
    if (Array.isArray(file)) {
      file.forEach(f => formData.append('files', f));
    } else {
      formData.append('files', file);
    }

    // Add type parameter
    const url = `${API_BASE_URL}/v1/upload/?type=${type}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const results = await response.json();

    // Backend returns an array of results
    // For single file, return the first result
    // For multiple files, return all results
    return Array.isArray(file) ? results : results[0];
  }

  // List uploaded files
  async getUploadedFiles() {
    const response = await fetch(`${API_BASE_URL}/v1/upload/files`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to fetch files');
    }

    return await response.json();
  }

  // Preview file
  async previewFile(filename) {
    const response = await fetch(`${API_BASE_URL}/v1/upload/preview/${filename}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to preview file');
    }

    return await response.json();
  }

  // Delete file
  async deleteFile(filename) {
    const response = await fetch(`${API_BASE_URL}/v1/upload/${filename}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to delete file');
    }

    return await response.json();
  }

  // Compute IRI (legacy - heavy processing)
  async computeIRI(filename, options = {}) {
    const params = new URLSearchParams();

    if (options.segmentLength) params.append('segment_length', options.segmentLength);
    if (options.cutoffFreq) params.append('cutoff_freq', options.cutoffFreq);

    const queryString = params.toString();
    const url = `${API_BASE_URL}/v1/iri/compute/${filename}${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'IRI computation failed');
    }

    return await response.json();
  }

  // Get cached IRI data (INSTANT - preferred method)
  async getCachedIRI(filename) {
    const response = await fetch(`${API_BASE_URL}/v1/iri/cached/${filename}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      // If cache not found, fall back to compute
      if (response.status === 404) {
        console.log('IRI cache not found, falling back to compute...');
        return await this.computeIRI(filename);
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get cached IRI');
    }

    return await response.json();
  }

  // Validate file
  async validateFile(filename) {
    const response = await fetch(`${API_BASE_URL}/v1/iri/validate/${filename}`);

    if (!response.ok) {
      throw new Error('File validation failed');
    }

    return await response.json();
  }

  // Get service status
  async getServiceStatus() {
    const response = await fetch(`${API_BASE_URL}/v1/iri/status`);

    if (!response.ok) {
      throw new Error('Failed to get service status');
    }

    return await response.json();
  }
}

export default new ApiService();

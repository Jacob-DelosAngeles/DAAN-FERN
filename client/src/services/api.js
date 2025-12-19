import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to add the auth token to headers
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const authService = {
    login: async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        const response = await api.post('/auth/login/access-token', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },
    register: async (email, password, fullName) => {
        const response = await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
        });
        return response.data;
    },
    logout: () => {
        localStorage.removeItem('token');
    },
    getCurrentUser: () => {
        return localStorage.getItem('token');
    },
    getUsers: async () => {
        const response = await api.get('/auth/users');
        return response.data;
    },
    updateUserRole: async (userId, role) => {
        const response = await api.put(`/auth/users/${userId}/role?role=${role}`);
        return response.data;
    },
};

export const fileService = {
    uploadFile: async (file, type = 'iri') => {
        const formData = new FormData();

        if (Array.isArray(file)) {
            file.forEach(f => formData.append('files', f));
        } else {
            formData.append('files', file);
        }

        try {
            const response = await api.post(`/upload/?type=${type}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            // Backend returns array, return first item if single file upload, else return all
            const data = response.data;
            return Array.isArray(file) ? { success: true, data } : (Array.isArray(data) ? data[0] : data);
        } catch (error) {
            console.error('Upload error:', error);
            // Enhanced error message
            const msg = error.response?.data?.detail
                ? (typeof error.response.data.detail === 'string' ? error.response.data.detail : JSON.stringify(error.response.data.detail))
                : 'Upload failed';
            return { success: false, message: msg };
        }
    },

    computeIRI: async (filename) => {
        try {
            const response = await api.post(`/iri/compute/${filename}`);
            return response.data;
        } catch (error) {
            console.error('IRI computation error:', error);
            return { success: false, message: error.response?.data?.detail || 'Computation failed' };
        }
    },

    // Get cached IRI data (INSTANT - preferred method)
    getCachedIRI: async (filename) => {
        try {
            const response = await api.get(`/iri/cached/${filename}`);
            return response.data;
        } catch (error) {
            // If cache not found (404), fall back to compute
            if (error.response?.status === 404) {
                console.log('IRI cache miss, falling back to compute...');
                return fileService.computeIRI(filename);
            }
            console.error('Cached IRI error:', error);
            return { success: false, message: error.response?.data?.detail || 'Failed to get IRI data' };
        }
    },

    processPotholes: async (filename) => {
        try {
            const response = await api.get(`/pothole/process/${filename}`);
            return response.data;
        } catch (error) {
            console.error('Pothole processing error:', error);
            return { success: false, message: error.response?.data?.detail || 'Processing failed' };
        }
    },

    processVehicles: async (filename) => {
        try {
            const response = await api.get(`/vehicle/process/${filename}`);
            return response.data;
        } catch (error) {
            console.error('Vehicle processing error:', error);
            return { success: false, message: error.response?.data?.detail || 'Processing failed' };
        }
    },

    processPavement: async (filename) => {
        try {
            const response = await api.get(`/pavement/process/${filename}`);
            return response.data;
        } catch (error) {
            console.error('Pavement processing error:', error);
            return { success: false, message: error.response?.data?.detail || 'Processing failed' };
        }
    },

    getUploadedFiles: async (category = null) => {
        try {
            const url = category ? `/upload/files/${category}` : '/upload/files';
            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Get files error:', error);
            return { success: false, message: error.response?.data?.detail || 'Failed to list files' };
        }
    },

    deleteFile: async (uploadId) => {
        try {
            const response = await api.delete(`/upload/${uploadId}`);
            return response.data;
        } catch (error) {
            console.error('Delete file error:', error);
            return { success: false, message: error.response?.data?.detail || 'Delete failed' };
        }
    }
};

export default api;

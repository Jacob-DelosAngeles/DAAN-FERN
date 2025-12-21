import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Store for the getToken function (not the token itself - tokens expire!)
let getTokenFunction = null;

// Function to set the getToken function from Clerk
export const setTokenGetter = (getTokenFn) => {
    getTokenFunction = getTokenFn;
};

// Legacy: set static token (for backwards compatibility)
export const setAuthToken = (token) => {
    // Store as backup in localStorage
    if (token) {
        localStorage.setItem('clerk_token_backup', token);
    }
};

// Add a request interceptor to add fresh auth token to headers
api.interceptors.request.use(
    async (config) => {
        let token = null;

        // Get fresh token from Clerk if available
        if (getTokenFunction) {
            try {
                token = await getTokenFunction();
            } catch (e) {
                console.warn('Failed to get fresh Clerk token:', e);
            }
        }

        // Fall back to localStorage for backwards compatibility
        if (!token) {
            token = localStorage.getItem('token') || localStorage.getItem('clerk_token_backup');
        }

        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Legacy auth service (kept for backwards compatibility during migration)
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
        currentAuthToken = null;
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
    // Sync user with backend (called after Clerk login)
    syncUser: async (clerkToken) => {
        try {
            const response = await api.post('/auth/sync', {}, {
                headers: {
                    'Authorization': `Bearer ${clerkToken}`
                }
            });
            return response.data;
        } catch (error) {
            console.error('User sync error:', error);
            throw error;
        }
    },

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

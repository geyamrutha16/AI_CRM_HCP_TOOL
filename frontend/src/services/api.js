import axios from 'axios';

/**
 * API Service for communicating with backend
 * Handles all HTTP requests to the FastAPI server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add request interceptor
api.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear auth and redirect to login if needed
            localStorage.removeItem('auth_token');
        }
        return Promise.reject(error);
    }
);

/**
 * Chat/Agent API
 */
export const agentAPI = {
    // Run agent with user message
    runAgent: async (message) => {
        const response = await api.post('/agent/run', { message });
        return response.data;
    },

    // Analyze sentiment of text
    analyzeSentiment: async (text) => {
        const response = await api.post('/agent/analyze', { text });
        return response.data;
    },

    // Health check
    healthCheck: async () => {
        const response = await api.get('/agent/health');
        return response.data;
    }
};

/**
 * Interactions API
 */
export const interactionsAPI = {
    // Get all interactions
    getAll: async (skip = 0, limit = 10, doctorName = null) => {
        const response = await api.get('/interaction', {
            params: { skip, limit, doctor_name: doctorName }
        });
        return response.data;
    },

    // Get single interaction
    getById: async (id) => {
        const response = await api.get(`/interaction/${id}`);
        return response.data;
    },

    // Create new interaction
    create: async (data) => {
        const response = await api.post('/interaction', data);
        return response.data;
    },

    // Update interaction
    update: async (id, data) => {
        const response = await api.put(`/interaction/${id}`, data);
        return response.data;
    },

    // Delete interaction
    delete: async (id) => {
        const response = await api.delete(`/interaction/${id}`);
        return response.data;
    }
};

/**
 * Health check
 */
export const systemAPI = {
    health: async () => {
        const response = await api.get('/health');
        return response.data;
    }
};

export default api;

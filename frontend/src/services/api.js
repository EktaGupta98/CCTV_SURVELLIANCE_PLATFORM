import axios from 'axios';

// relative base URL. Automatically works via Vite proxy in development and Nginx proxy in production.
const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Video uploads
  uploadVideo: async (formData) => {
    const response = await apiClient.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Video listings
  getVideos: async () => {
    const response = await apiClient.get('/videos');
    return response.data;
  },

  // Processing job status
  getProcessingStatus: async (jobId) => {
    const response = await apiClient.get(`/processing/${jobId}`);
    return response.data;
  },

  // Camera listings
  getCameras: async () => {
    const response = await apiClient.get('/cameras');
    return response.data;
  },

  // Entities listings
  getEntities: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/entities', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Entity Details
  getEntityDetails: async (entityId) => {
    const response = await apiClient.get(`/entities/${entityId}`);
    return response.data;
  },

  // Entity Tracking logs
  getEntityHistory: async (entityId) => {
    const response = await apiClient.get(`/entities/${entityId}/history`);
    return response.data;
  },

  // Entity Map markers and polylines
  getEntityMapPath: async (entityId) => {
    const response = await apiClient.get(`/entities/${entityId}/map`);
    return response.data;
  },

  // Search and Filter entities history
  searchHistory: async (searchFilters) => {
    const response = await apiClient.post('/search', searchFilters);
    return response.data;
  },

  // Tracks listing
  getTracks: async () => {
    const response = await apiClient.get('/tracks');
    return response.data;
  },

  // Health check
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default api;

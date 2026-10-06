import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const getApiBaseUrl = () => {
  // Use the VITE environment variable for production/frontend deployments
  // Falls back to '/api' for local development or monolithic deployments
  return import.meta.env.VITE_API_BASE_URL || '/api';
};

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const authStore = useAuthStore();
    
    const isLoginRequest = error.config && error.config.url && error.config.url.endsWith('/login');

    if (error.response && error.response.status === 401 && !isLoginRequest) {
      console.warn('Token expired or unauthorized. Logging out...');
      authStore.logout();
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
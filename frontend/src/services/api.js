import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const DEFAULT_PROD_BACKEND = 'https://antibioticplay-backend-lkxx.onrender.com/api';

const getApiBaseUrl = () => {
  let raw = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');

  // Auto-correct legacy Render backend URL without the '-lkxx' suffix
  if (raw.includes('antibioticplay-backend.onrender.com')) {
    raw = raw.replace(
      'antibioticplay-backend.onrender.com',
      'antibioticplay-backend-lkxx.onrender.com'
    );
  }

  if (!raw) {
    const isLocal =
      typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    return isLocal ? '/api' : DEFAULT_PROD_BACKEND;
  }

  return raw.endsWith('/api') ? raw : `${raw}/api`;
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
      config.headers.Authorization = `Bearer ${token}`;
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

    const isLoginRequest =
      error.config && error.config.url && error.config.url.endsWith('/login');

    if (error.response && error.response.status === 401 && !isLoginRequest) {
      console.warn('Token expired or unauthorized. Logging out...');
      authStore.logout();
    }

    return Promise.reject(error);
  }
);

export default apiClient;

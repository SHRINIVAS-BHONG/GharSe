import axios from 'axios';

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const API_BASE_URL = rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl.replace(/\/$/, '')}/api`;

export const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gharse_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Surfaces a friendly message string from any API error.
export function apiErrorMessage(err) {
  if (!err?.response) {
    return 'Cannot connect to backend server. Make sure the server is running.';
  }
  return (
    err.response.data?.detail ||
    err.response.data?.message ||
    (err.response.status >= 500
      ? 'Database connection error. Please make sure MongoDB is running.'
      : 'Something went wrong. Please try again.')
  );
}

export const UPLOADS_BASE_URL = API_BASE_URL.replace(/\/api$/, '');

export function imageUrl(path) {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${UPLOADS_BASE_URL}${path}`;
}

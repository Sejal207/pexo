import axios from 'axios';
import { store } from '../app/store';
import { logout } from '../features/auth/authSlice';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const httpClient = axios.create({
  baseURL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// The access token lives only in memory — never in localStorage/sessionStorage —
// so it disappears on tab close and can't be read by a persisted-storage XSS payload.
let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

// The gateway only proxies business endpoints under /api/v1/* — /auth/* lives
// at the root instead. Every call site across the app writes paths like
// '/employees/' with neither prefix; add /api/v1 here, once, rather than at
// every call site (and rather than baking it into baseURL, which would break
// /auth/* the same way).
const API_PREFIX = '/api/v1';

httpClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  if (config.url && !config.url.startsWith('/auth') && !config.url.startsWith(API_PREFIX)) {
    config.url = `${API_PREFIX}${config.url}`;
  }
  return config;
});

const AUTH_ENDPOINTS = ['/auth/login', '/auth/refresh', '/auth/logout'];

let refreshPromise = null;

const refreshAccessToken = async () => {
  if (!refreshPromise) {
    refreshPromise = httpClient.post('/auth/refresh')
      .then(({ data }) => {
        setAccessToken(data.access_token);
        return data;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
};

httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    const isAuthEndpoint = config && AUTH_ENDPOINTS.some((path) => config.url?.includes(path));

    if (response?.status === 401 && config && !config._retried && !isAuthEndpoint) {
      config._retried = true;
      try {
        await refreshAccessToken();
        return httpClient(config);
      } catch (refreshError) {
        setAccessToken(null);
        store.dispatch(logout());
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

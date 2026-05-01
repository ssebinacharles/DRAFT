import axios from 'axios';

// Connects to your Django backend. Next.js pulls this from your .env.local file.
// Fallback is localhost:8000 (Django's default port) if the env variable is missing.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- REQUEST INTERCEPTOR ---
// Automatically attach the auth token to every request
apiClient.interceptors.request.use(
  (config) => {
    // Assuming your AuthContext saves the token to localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`; // Or 'Token ${token}' depending on your Django setup
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- RESPONSE INTERCEPTOR ---
// Globally catch 401 Unauthorized errors (e.g., token expired)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Authentication expired. Redirecting to login.');
      // Optional: Clear token and kick user to login page
      // localStorage.removeItem('token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
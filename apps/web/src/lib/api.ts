import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auth API
export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

// Conversations API
export const getConversations = async () => {
  // TODO: Connect to backend API when ready
  const response = await api.get('/conversations');
  return response.data;
};

export const getMessages = async (phone: string) => {
  // TODO: Connect to backend API when ready
  const response = await api.get(`/conversations/${phone}/messages`);
  return response.data;
};

// Handoff API
export const takeControl = async (phone: string) => {
  // TODO: Connect to backend API when ready
  const response = await api.post(`/conversations/${phone}/take-control`);
  return response.data;
};

export const returnToBot = async (phone: string) => {
  // TODO: Connect to backend API when ready
  const response = await api.post(`/conversations/${phone}/return-to-bot`);
  return response.data;
};

export const sendManualMessage = async (phone: string, message: string) => {
  // TODO: Connect to backend API when ready
  const response = await api.post(`/conversations/${phone}/send`, { message });
  return response.data;
};

export default api;

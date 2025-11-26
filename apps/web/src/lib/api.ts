import axios from 'axios';
import type { Config, Conversation, Message, User, CollectedData, RAGStats, APIResponse } from '@/types';

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

// Add response interceptor to handle 401 errors (token expiration)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;

          // Save new tokens
          localStorage.setItem('token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }

          // Update the failed request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;

          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const login = async (email: string, password: string) => {
  // Supabase expects JSON with email (not form data)
  const response = await api.post('/auth/login', {
    email,
    password,
  });
  return response.data;
};

// Configuration API
export const getConfig = async (): Promise<Config> => {
  const response = await api.get('/config/');
  // API returns { configs: {...} }
  return response.data.configs || response.data;
};

export const saveConfig = async (config: Partial<Config>): Promise<APIResponse> => {
  // Backend expects: { configs: { key: value, ... } }
  const response = await api.put('/config/', { configs: config });
  return response.data;
};

export const uploadRAGDocuments = async (files: File[]): Promise<{ status: string; uploaded: number; total_chunks: number; message: string; error?: string }> => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  const response = await api.post('/rag/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const clearRAGCollection = async (): Promise<{ status: string; message: string; error?: string }> => {
  const response = await api.delete('/rag/clear');
  return response.data;
};

export const getRAGStats = async (): Promise<RAGStats> => {
  const response = await api.get('/rag/stats');
  return response.data;
};

export const previewVoice = async (voice: string): Promise<Blob> => {
  const response = await api.post('/tts/preview', { voice }, {
    responseType: 'blob',
  });
  return response.data;
};

// Conversations API
export const getConversations = async (): Promise<Conversation[]> => {
  const response = await api.get('/conversations/');
  // API returns flat objects, transform to match Conversation type
  return response.data.map((item: any) => ({
    user: {
      id: item.id || 0,
      phone: item.phone,
      name: item.name,
      email: item.email,
      conversation_mode: item.mode || 'AUTO',
      total_messages: item.total_messages || 0,
      last_message_at: item.timestamp,
      sentiment: item.sentiment,
      stage: item.stage,
      conversation_summary: item.conversation_summary
    },
    last_message: item.lastMessage || '',
    unread: item.unread || false
  }));
};

export const getMessages = async (phone: string): Promise<Message[]> => {
  const response = await api.get(`/conversations/${phone}/messages`);
  return response.data;
};

export const getUserInfo = async (userId: number): Promise<User> => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export const getUserByPhone = async (phone: string): Promise<User> => {
  // Use the conversations endpoint which returns user details
  const response = await api.get(`/conversations/${phone}`);
  return response.data;
};

// Handoff API
export const takeControl = async (phone: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/take`, {});
  return response.data;
};


export const returnToBot = async (phone: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/return`);
  return response.data;
};

export const sendManualMessage = async (phone: string, message: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/send`, { message });
  return response.data;
};

// Test Chat API
export const processTestMessage = async (
  phone: string,
  message: string,
  history: Message[]
): Promise<any> => {
  // Transform frontend Message[] to backend HistoryMessage[] format
  // Frontend has 'message_text', backend expects 'text'
  const transformedHistory = history.map(msg => ({
    text: msg.message_text,  // Convert message_text → text
    sender: msg.sender
  }));

  const response = await api.post('/bot/process', {
    phone,
    message,
    history: transformedHistory,  // Send transformed history
  });
  // Backend returns direct response object: { response, user_phone, user_name, intent_score, sentiment, stage, conversation_mode }
  return response.data;
};

export const clearTestConversation = async (phone: string): Promise<APIResponse> => {
  const response = await api.delete(`/conversations/${phone}/clear`);
  return response.data;
};

export default api;

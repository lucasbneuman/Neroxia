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
  return response.data;
};

export const saveConfig = async (config: Partial<Config>): Promise<APIResponse> => {
  const response = await api.put('/config/', config);
  return response.data;
};

export const uploadRAGDocuments = async (files: File[]): Promise<APIResponse<{ uploaded: number; total_chunks: number }>> => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  const response = await api.post('/config/rag/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const clearRAGCollection = async (): Promise<APIResponse> => {
  const response = await api.delete('/config/rag/clear');
  return response.data;
};

export const getRAGStats = async (): Promise<RAGStats> => {
  const response = await api.get('/config/rag/stats');
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
  const response = await api.get('/conversations');
  return response.data;
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
  const response = await api.get(`/users/phone/${phone}`);
  return response.data;
};

// Handoff API
export const takeControl = async (phone: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/take`);
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

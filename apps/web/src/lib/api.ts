import axios from 'axios';
import type { AxiosError } from 'axios';
import type { Config, Conversation, Message, User, RAGStats, APIResponse, Deal, JsonObject, WebWidgetConfig } from '@/types';

interface ApiErrorPayload {
  detail?: string;
  message?: string;
}

interface ConversationListItem {
  id?: number;
  phone: string | null;
  name?: string;
  email?: string;
  mode?: User['conversation_mode'];
  total_messages?: number;
  timestamp?: string;
  sentiment?: string;
  stage?: string;
  conversation_summary?: string;
  channel?: User['channel'];
  channel_user_id?: string;
  displayIdentifier?: string;
  originHost?: string;
  lastMessage?: string;
  unread?: boolean;
}

interface TestMessageResponse {
  response: string;
  user_phone?: string;
  user_name?: string | null;
  intent_score?: number;
  sentiment?: string;
  stage?: string;
  conversation_mode?: string;
}

export function getErrorMessage(error: unknown, fallback: string): string {
  const apiError = error as AxiosError<ApiErrorPayload>;
  return apiError.response?.data?.detail || apiError.response?.data?.message || fallback;
}

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

    // Only log detailed errors if they exist
    if (error.response || error.request) {
      console.error("API Error Details:", {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: error.response?.data,
        url: originalRequest?.url,
        method: originalRequest?.method,
      });
    }

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

export const signup = async (email: string, password: string, name: string) => {
  const response = await api.post('/auth/signup', {
    email,
    password,
    name,
  });
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/auth/logout');
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
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
  const response = await api.get<ConversationListItem[]>('/conversations/');
  // API returns flat objects, transform to match Conversation type
  return response.data.map((item) => ({
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
      conversation_summary: item.conversation_summary,
      // Multi-channel support
      channel: item.channel || 'whatsapp',
      channel_user_id: item.channel_user_id,
      display_identifier: item.displayIdentifier,
      origin_host: item.originHost,
    },
    last_message: item.lastMessage || '',
    unread: item.unread || false
  }));
};

export const getMessages = async (phone: string): Promise<Message[]> => {
  const response = await api.get(`/conversations/${phone}/messages`);
  return response.data;
};

export const getConversationById = async (userId: number): Promise<User> => {
  const response = await api.get(`/conversations/id/${userId}`);
  return response.data;
};

export const getMessagesByUserId = async (userId: number): Promise<Message[]> => {
  const response = await api.get(`/conversations/id/${userId}/messages`);
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

export const takeControlByUserId = async (userId: number): Promise<APIResponse> => {
  const response = await api.post(`/handoff/id/${userId}/take`, {});
  return response.data;
};


export const returnToBot = async (phone: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/return`);
  return response.data;
};

export const returnToBotByUserId = async (userId: number): Promise<APIResponse> => {
  const response = await api.post(`/handoff/id/${userId}/return`);
  return response.data;
};

export const sendManualMessage = async (phone: string, message: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/${phone}/send`, { message });
  return response.data;
};

export const sendManualMessageByUserId = async (userId: number, message: string): Promise<APIResponse> => {
  const response = await api.post(`/handoff/id/${userId}/send`, { message });
  return response.data;
};

// Test Chat API
export const processTestMessage = async (
  phone: string,
  message: string,
  history: Message[]
): Promise<TestMessageResponse> => {
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

// CRM API
export const getCrmMetrics = async () => {
  const response = await api.get('/crm/dashboard/metrics');
  return response.data;
};

export const getDeals = async (stage?: string) => {
  const response = await api.get('/crm/deals', { params: { stage } });
  return response.data;
};


export const updateDealStage = async (dealId: number, stage: string) => {
  const response = await api.patch(`/crm/deals/${dealId}/stage`, { stage });
  return response.data;
};

export const updateDeal = async (dealId: number, data: Partial<Deal>) => {
  const response = await api.patch(`/crm/deals/${dealId}`, data);
  return response.data;
};

// Notes API
export const getNotes = async (userId: number) => {
  const response = await api.get(`/crm/users/${userId}/notes`);
  return response.data;
};

export const createNote = async (userId: number, content: string, createdBy: string, dealId?: number, noteType: string = 'note') => {
  const response = await api.post(`/crm/users/${userId}/notes`, {
    content,
    created_by: createdBy,
    deal_id: dealId,
    note_type: noteType
  });
  return response.data;
};

export const deleteNote = async (noteId: number) => {
  const response = await api.delete(`/crm/notes/${noteId}`);
  return response.data;
};

// Tags API
export const getTags = async () => {
  const response = await api.get('/crm/tags');
  return response.data;
};

export const createTag = async (name: string, color: string) => {
  const response = await api.post('/crm/tags', { name, color });
  return response.data;
};

export const getUserTags = async (userId: number) => {
  const response = await api.get(`/crm/users/${userId}/tags`);
  return response.data;
};

export const addTagToUser = async (userId: number, tagId: number) => {
  const response = await api.post(`/crm/users/${userId}/tags/${tagId}`);
  return response.data;
};

export const removeTagFromUser = async (userId: number, tagId: number) => {
  const response = await api.delete(`/crm/users/${userId}/tags/${tagId}`);
  return response.data;
};

// Delete conversation
export async function deleteConversation(phone: string, deleteFromCRM: boolean = false): Promise<{ status: string; message: string; messages_deleted: number; deals_deleted: number; crm_deleted: boolean }> {
  const response = await api.delete(`/conversations/${phone}`, {
    params: { delete_from_crm: deleteFromCRM }
  });
  return response.data;
}

export async function deleteConversationByUserId(userId: number, deleteFromCRM: boolean = false): Promise<{ status: string; message: string; messages_deleted: number; deals_deleted: number; crm_deleted: boolean }> {
  const response = await api.delete(`/conversations/id/${userId}`, {
    params: { delete_from_crm: deleteFromCRM }
  });
  return response.data;
}

// User Profile API
export const getUserProfile = async () => {
  const response = await api.get('/users/profile');
  return response.data;
};

export const updateUserProfile = async (data: {
  company_name?: string;
  phone?: string;
  timezone?: string;
  language?: string;
}) => {
  const response = await api.put('/users/profile', data);
  return response.data;
};

export const uploadAvatar = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/users/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getUserSettings = async () => {
  const response = await api.get('/users/settings');
  return response.data;
};

export const updateUserSettings = async (preferences: JsonObject) => {
  const response = await api.put('/users/settings', { preferences });
  return response.data;
};

export const changePassword = async (currentPassword: string, newPassword: string) => {
  const response = await api.put('/users/password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

export const deleteAccount = async () => {
  const response = await api.delete('/users/account');
  return response.data;
};

export const completeOnboarding = async () => {
  const response = await api.post('/users/onboarding/complete');
  return response.data;
};

export const updateOnboardingStep = async (step: number) => {
  const response = await api.put(`/users/onboarding/step?step=${step}`);
  return response.data;
};

// Subscription API
export const getSubscriptionPlans = async () => {
  const response = await api.get('/subscriptions/plans');
  return response.data;
};

export const getCurrentSubscription = async () => {
  const response = await api.get('/subscriptions/current');
  return response.data;
};

export const getSubscriptionUsage = async () => {
  const response = await api.get('/subscriptions/usage');
  return response.data;
};

export const getBillingHistory = async () => {
  const response = await api.get('/subscriptions/billing-history');
  return response.data;
};

export const cancelSubscription = async (cancelAtPeriodEnd: boolean = true) => {
  const response = await api.post('/subscriptions/cancel', {
    cancel_at_period_end: cancelAtPeriodEnd,
  });
  return response.data;
};

// Integrations API
export const getHubSpotStatus = async () => {
  const response = await api.get('/integrations/hubspot/status');
  return response.data;
};

export const getTwilioStatus = async () => {
  const response = await api.get('/integrations/twilio/status');
  return response.data;
};

export const getWebWidgetConfig = async (): Promise<WebWidgetConfig> => {
  const response = await api.get('/integrations/web-widget');
  return response.data;
};

export const updateWebWidgetConfig = async (payload: {
  enabled: boolean;
  allowed_origins: string[];
  default_primary_color: string;
}): Promise<WebWidgetConfig> => {
  const response = await api.put('/integrations/web-widget', payload);
  return response.data;
};

export const regenerateWebWidgetCredentials = async (): Promise<WebWidgetConfig> => {
  const response = await api.post('/integrations/web-widget/regenerate');
  return response.data;
};

export default api;

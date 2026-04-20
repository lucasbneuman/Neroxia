import { create } from 'zustand';
import type { JsonObject } from '@/types';

interface UserProfile {
  id: number;
  auth_user_id: string;
  company_name: string | null;
  phone: string | null;
  timezone: string;
  language: string;
  avatar_url: string | null;
  role: string;
  onboarding_completed: boolean;
  preferences: JsonObject;
}

interface Subscription {
  id: number;
  status: string;
  plan: {
    name: string;
    display_name: string;
  };
  current_period_end: string;
  cancel_at_period_end: boolean;
}

interface UserState {
  profile: UserProfile | null;
  subscription: Subscription | null;
  loading: boolean;
  setProfile: (profile: UserProfile) => void;
  setSubscription: (subscription: Subscription) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
  setLoading: (loading: boolean) => void;
  clearUser: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  profile: null,
  subscription: null,
  loading: false,
  setProfile: (profile) => set({ profile }),
  setSubscription: (subscription) => set({ subscription }),
  updateProfile: (updates) =>
    set((state) => ({
      profile: state.profile ? { ...state.profile, ...updates } : null,
    })),
  setLoading: (loading) => set({ loading }),
  clearUser: () => set({ profile: null, subscription: null }),
}));

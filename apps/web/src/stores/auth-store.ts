import { create } from 'zustand';

interface AuthState {
    token: string | null;
    isAuthenticated: boolean;
    setToken: (token: string) => void;
    logout: () => void;
    initializeAuth: () => void;
}

// Helper to get token from localStorage safely
const getStoredToken = (): string | null => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token');
    }
    return null;
};

export const useAuthStore = create<AuthState>((set) => ({
    token: getStoredToken(),
    isAuthenticated: !!getStoredToken(),
    setToken: (token: string) => {
        if (typeof window !== 'undefined') {
            localStorage.setItem('token', token);
        }
        set({ token, isAuthenticated: true });
    },
    logout: () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
        }
        set({ token: null, isAuthenticated: false });
    },
    initializeAuth: () => {
        const token = getStoredToken();
        set({ token, isAuthenticated: !!token });
    },
}));

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { login } from '@/lib/api';
import { useAuthStore } from '@/stores/auth-store';

export default function LoginPage() {
    const router = useRouter();
    const setToken = useAuthStore((state) => state.setToken);
    const { addToast } = useToast();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = await login(email, password);
            // Save both access token and refresh token
            setToken(data.access_token);
            if (data.refresh_token) {
                localStorage.setItem('refresh_token', data.refresh_token);
            }
            addToast('¡Inicio de sesión exitoso!', 'success');
            router.push('/dashboard/chat');
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || 'Error al iniciar sesión. Por favor, intenta de nuevo.';
            addToast(errorMessage, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-purple-50">
            <div className="max-w-md w-full space-y-8 p-10 bg-white dark:bg-gray-800 rounded-3xl shadow-large border-2 border-gray-200 dark:border-gray-700">
                <div>
                    <h1 className="text-center text-4xl font-black text-black dark:text-white tracking-tight">
                        Neroxia
                    </h1>
                    <div className="mt-2 flex items-center justify-center">
                        <div className="h-1 w-16 bg-gradient-to-r from-purple-600 to-purple-500 rounded-full"></div>
                    </div>
                    <p className="mt-4 text-center text-sm text-gray-600 font-bold">
                        Intelligent Sales Automation
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="email" className="block text-sm font-bold text-black dark:text-white mb-2">
                                Email
                            </label>
                            <Input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="admin@example.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-bold text-black dark:text-white mb-2">
                                Password
                            </label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                            />
                        </div>
                    </div>

                    <Button
                        type="submit"
                        disabled={loading}
                        className="w-full"
                        size="lg"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <LoadingSpinner size="sm" variant="default" />
                                Iniciando sesión...
                            </span>
                        ) : (
                            'Iniciar Sesión'
                        )}
                    </Button>
                </form>

                <div className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        ¿No tienes cuenta?{' '}
                        <Link href="/signup" className="font-bold text-purple-600 hover:text-purple-500">
                            Regístrate gratis
                        </Link>
                    </p>
                </div>

                <div className="text-center text-xs text-gray-500 font-bold">
                    © 2025 Neroxia. All rights reserved.
                </div>
            </div>
        </div>
    );
}

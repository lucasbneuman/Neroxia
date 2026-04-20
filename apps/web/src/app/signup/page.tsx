'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { getErrorMessage, signup } from '@/lib/api';
import { useAuthStore } from '@/stores/auth-store';

export default function SignupPage() {
    const router = useRouter();
    const setToken = useAuthStore((state) => state.setToken);
    const { addToast } = useToast();

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate passwords match
        if (formData.password !== formData.confirmPassword) {
            addToast('Las contraseñas no coinciden', 'error');
            return;
        }

        // Validate password strength
        if (formData.password.length < 8) {
            addToast('La contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }

        setLoading(true);

        try {
            const data = await signup(formData.email, formData.password, formData.name);

            // Save tokens
            setToken(data.access_token);
            if (data.refresh_token) {
                localStorage.setItem('refresh_token', data.refresh_token);
            }

            addToast('¡Cuenta creada exitosamente!', 'success');

            // Redirect to onboarding
            router.push('/onboarding');
        } catch (error) {
            addToast(getErrorMessage(error, 'Error al crear la cuenta. Por favor, intenta de nuevo.'), 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-purple-50">
            <div className="max-w-md w-full space-y-8 p-10 bg-white dark:bg-gray-800 rounded-3xl shadow-large border-2 border-gray-200 dark:border-gray-700">
                <div>
                    <h1 className="text-center text-4xl font-black text-black dark:text-white tracking-tight">
                        Sales Oracle
                    </h1>
                    <div className="mt-2 flex items-center justify-center">
                        <div className="h-1 w-16 bg-gradient-to-r from-purple-600 to-purple-500 rounded-full"></div>
                    </div>
                    <p className="mt-4 text-center text-sm text-gray-600 font-bold">
                        Crear una cuenta nueva
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="name" className="block text-sm font-bold text-black dark:text-white mb-2">
                                Nombre completo
                            </label>
                            <Input
                                id="name"
                                name="name"
                                type="text"
                                required
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Juan Pérez"
                            />
                        </div>

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
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="juan@empresa.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-bold text-black dark:text-white mb-2">
                                Contraseña
                            </label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="new-password"
                                required
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Mínimo 8 caracteres"
                            />
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-bold text-black dark:text-white mb-2">
                                Confirmar contraseña
                            </label>
                            <Input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                autoComplete="new-password"
                                required
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Repite tu contraseña"
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
                                Creando cuenta...
                            </span>
                        ) : (
                            'Crear cuenta'
                        )}
                    </Button>
                </form>

                <div className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        ¿Ya tienes una cuenta?{' '}
                        <Link href="/login" className="font-bold text-purple-600 hover:text-purple-500">
                            Inicia sesión
                        </Link>
                    </p>
                </div>

                <div className="text-center text-xs text-gray-500 font-bold">
                    © 2025 Sales Oracle. All rights reserved.
                </div>
            </div>
        </div>
    );
}

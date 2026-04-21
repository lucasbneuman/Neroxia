'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { getUserProfile, updateUserProfile, uploadAvatar, changePassword, deleteAccount } from '@/lib/api';
import { useUserStore } from '@/stores/user-store';
import { User, Building2, Globe, MapPin, Lock, Trash2, Camera } from 'lucide-react';

export default function ProfilePage() {
    const { addToast } = useToast();
    const { profile, setProfile } = useUserStore();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'danger'>('profile');

    const [formData, setFormData] = useState({
        company_name: '',
        phone: '',
        timezone: 'UTC',
        language: 'es',
    });

    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const data = await getUserProfile();
            setProfile(data);
            setFormData({
                company_name: data.company_name || '',
                phone: data.phone || '',
                timezone: data.timezone || 'UTC',
                language: data.language || 'es',
            });
        } catch (error) {
            addToast('Error al cargar perfil', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPasswordData({
            ...passwordData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSaveProfile = async () => {
        setSaving(true);
        try {
            await updateUserProfile(formData);
            addToast('Perfil actualizado exitosamente', 'success');
            loadProfile();
        } catch (error: any) {
            addToast(error.response?.data?.detail || 'Error al guardar', 'error');
        } finally {
            setSaving(false);
        }
    };

    const handleChangePassword = async () => {
        if (passwordData.new_password !== passwordData.confirm_password) {
            addToast('Las contraseñas no coinciden', 'error');
            return;
        }

        if (passwordData.new_password.length < 8) {
            addToast('La contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }

        setSaving(true);
        try {
            await changePassword(passwordData.current_password, passwordData.new_password);
            addToast('Contraseña cambiada exitosamente', 'success');
            setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
        } catch (error: any) {
            addToast(error.response?.data?.detail || 'Error al cambiar contraseña', 'error');
        } finally {
            setSaving(false);
        }
    };

    const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file size (max 2MB)
        if (file.size > 2 * 1024 * 1024) {
            addToast('La imagen debe ser menor a 2MB', 'error');
            return;
        }

        try {
            await uploadAvatar(file);
            addToast('Avatar actualizado', 'success');
            loadProfile();
        } catch (error) {
            addToast('Error al subir imagen', 'error');
        }
    };

    const handleDeleteAccount = async () => {
        if (!confirm('¿Estás seguro? Esta acción es irreversible y eliminará todos tus datos.')) {
            return;
        }

        const confirmation = prompt('Escribe "ELIMINAR" para confirmar:');
        if (confirmation !== 'ELIMINAR') {
            addToast('Cancelado', 'error');
            return;
        }

        setSaving(true);
        try {
            await deleteAccount();
            addToast('Cuenta eliminada', 'success');
            window.location.href = '/login';
        } catch (error: any) {
            addToast(error.response?.data?.detail || 'Error al eliminar cuenta', 'error');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-black dark:text-white">Mi Perfil</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Administra tu información personal y configuración de cuenta
                </p>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
                <div className="flex gap-4">
                    <button
                        onClick={() => setActiveTab('profile')}
                        className={`pb-4 px-2 font-semibold border-b-2 transition ${
                            activeTab === 'profile'
                                ? 'border-purple-600 text-purple-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        <User className="w-4 h-4 inline mr-2" />
                        Perfil
                    </button>
                    <button
                        onClick={() => setActiveTab('security')}
                        className={`pb-4 px-2 font-semibold border-b-2 transition ${
                            activeTab === 'security'
                                ? 'border-purple-600 text-purple-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        <Lock className="w-4 h-4 inline mr-2" />
                        Seguridad
                    </button>
                    <button
                        onClick={() => setActiveTab('danger')}
                        className={`pb-4 px-2 font-semibold border-b-2 transition ${
                            activeTab === 'danger'
                                ? 'border-red-600 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        <Trash2 className="w-4 h-4 inline mr-2" />
                        Zona de peligro
                    </button>
                </div>
            </div>

            {/* Profile Tab */}
            {activeTab === 'profile' && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="space-y-6">
                        {/* Avatar */}
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                Foto de perfil
                            </label>
                            <div className="flex items-center gap-4">
                                <div className="w-20 h-20 rounded-full bg-purple-100 flex items-center justify-center text-2xl font-bold text-purple-600">
                                    {profile?.company_name?.[0] || 'U'}
                                </div>
                                <label className="cursor-pointer">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleAvatarUpload}
                                        className="hidden"
                                    />
                                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
                                        <Camera className="w-4 h-4" />
                                        <span className="text-sm font-semibold">Cambiar foto</span>
                                    </div>
                                </label>
                            </div>
                        </div>

                        {/* Company Name */}
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                <Building2 className="w-4 h-4 inline mr-1" />
                                Nombre de la empresa
                            </label>
                            <Input
                                name="company_name"
                                value={formData.company_name}
                                onChange={handleChange}
                                placeholder="Mi Empresa S.A."
                            />
                        </div>

                        {/* Phone */}
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                Teléfono
                            </label>
                            <Input
                                name="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={handleChange}
                                placeholder="+52 55 1234 5678"
                            />
                        </div>

                        {/* Timezone */}
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                <MapPin className="w-4 h-4 inline mr-1" />
                                Zona horaria
                            </label>
                            <select
                                name="timezone"
                                value={formData.timezone}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                            >
                                <option value="America/Mexico_City">México (GMT-6)</option>
                                <option value="America/New_York">Nueva York (GMT-5)</option>
                                <option value="America/Los_Angeles">Los Ángeles (GMT-8)</option>
                                <option value="America/Bogota">Bogotá (GMT-5)</option>
                                <option value="America/Argentina/Buenos_Aires">Buenos Aires (GMT-3)</option>
                                <option value="Europe/Madrid">Madrid (GMT+1)</option>
                                <option value="UTC">UTC (GMT+0)</option>
                            </select>
                        </div>

                        {/* Language */}
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                <Globe className="w-4 h-4 inline mr-1" />
                                Idioma
                            </label>
                            <select
                                name="language"
                                value={formData.language}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                            >
                                <option value="es">Español</option>
                                <option value="en">English</option>
                            </select>
                        </div>

                        <Button onClick={handleSaveProfile} disabled={saving} className="w-full">
                            {saving ? (
                                <span className="flex items-center gap-2">
                                    <LoadingSpinner size="sm" variant="default" />
                                    Guardando...
                                </span>
                            ) : (
                                'Guardar cambios'
                            )}
                        </Button>
                    </div>
                </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <h2 className="text-xl font-bold mb-4">Cambiar contraseña</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                Contraseña actual
                            </label>
                            <Input
                                name="current_password"
                                type="password"
                                value={passwordData.current_password}
                                onChange={handlePasswordChange}
                                placeholder="Tu contraseña actual"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                Nueva contraseña
                            </label>
                            <Input
                                name="new_password"
                                type="password"
                                value={passwordData.new_password}
                                onChange={handlePasswordChange}
                                placeholder="Mínimo 8 caracteres"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-black dark:text-white mb-2">
                                Confirmar nueva contraseña
                            </label>
                            <Input
                                name="confirm_password"
                                type="password"
                                value={passwordData.confirm_password}
                                onChange={handlePasswordChange}
                                placeholder="Repite la nueva contraseña"
                            />
                        </div>

                        <Button onClick={handleChangePassword} disabled={saving} className="w-full">
                            {saving ? (
                                <span className="flex items-center gap-2">
                                    <LoadingSpinner size="sm" variant="default" />
                                    Cambiando...
                                </span>
                            ) : (
                                'Cambiar contraseña'
                            )}
                        </Button>
                    </div>
                </div>
            )}

            {/* Danger Zone Tab */}
            {activeTab === 'danger' && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-red-200 p-6">
                    <h2 className="text-xl font-bold text-red-600 mb-2">Eliminar cuenta</h2>
                    <p className="text-gray-600 mb-4">
                        Esta acción es permanente e irreversible. Se eliminarán todos tus datos, conversaciones,
                        configuraciones y suscripciones.
                    </p>
                    <Button onClick={handleDeleteAccount} disabled={saving} variant="outline" className="border-red-600 text-red-600 hover:bg-red-50">
                        {saving ? (
                            <span className="flex items-center gap-2">
                                <LoadingSpinner size="sm" variant="default" />
                                Eliminando...
                            </span>
                        ) : (
                            <>
                                <Trash2 className="w-4 h-4 mr-2" />
                                Eliminar mi cuenta
                            </>
                        )}
                    </Button>
                </div>
            )}
        </div>
    );
}

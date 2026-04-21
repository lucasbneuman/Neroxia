'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { updateUserProfile, updateOnboardingStep, completeOnboarding } from '@/lib/api';
import { Check, ChevronRight, Building2, MapPin, Globe, Rocket } from 'lucide-react';

const STEPS = [
    { id: 1, title: 'Información de empresa', icon: Building2 },
    { id: 2, title: 'Configuración regional', icon: MapPin },
    { id: 3, title: 'Selecciona tu plan', icon: Rocket },
    { id: 4, title: '¡Todo listo!', icon: Check },
];

export default function OnboardingPage() {
    const router = useRouter();
    const { addToast } = useToast();
    const [currentStep, setCurrentStep] = useState(1);
    const [loading, setLoading] = useState(false);

    const [formData, setFormData] = useState({
        company_name: '',
        phone: '',
        timezone: 'America/Mexico_City',
        language: 'es',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleNext = async () => {
        if (currentStep === 1) {
            // Validate step 1
            if (!formData.company_name || !formData.phone) {
                addToast('Por favor completa todos los campos', 'error');
                return;
            }
        }

        setLoading(true);
        try {
            // Save progress to backend
            await updateOnboardingStep(currentStep + 1);

            // If moving from step 1, save profile data
            if (currentStep === 1) {
                await updateUserProfile({
                    company_name: formData.company_name,
                    phone: formData.phone,
                });
            }

            // If moving from step 2, save regional settings
            if (currentStep === 2) {
                await updateUserProfile({
                    timezone: formData.timezone,
                    language: formData.language,
                });
            }

            setCurrentStep(currentStep + 1);
        } catch (error: any) {
            addToast('Error al guardar. Por favor intenta de nuevo.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleFinish = async () => {
        setLoading(true);
        try {
            await completeOnboarding();
            addToast('¡Configuración completada!', 'success');
            router.push('/dashboard');
        } catch (error: any) {
            addToast('Error al completar la configuración', 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-black text-black tracking-tight mb-2">
                        Bienvenido a Neroxia
                    </h1>
                    <p className="text-gray-600">Configuremos tu cuenta en 4 pasos simples</p>
                </div>

                {/* Progress Steps */}
                <div className="mb-12">
                    <div className="flex items-center justify-between">
                        {STEPS.map((step, index) => {
                            const Icon = step.icon;
                            const isCompleted = currentStep > step.id;
                            const isCurrent = currentStep === step.id;

                            return (
                                <div key={step.id} className="flex items-center flex-1">
                                    <div className="flex flex-col items-center flex-1">
                                        <div
                                            className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all ${
                                                isCompleted
                                                    ? 'bg-purple-600 border-purple-600 text-white'
                                                    : isCurrent
                                                    ? 'bg-white border-purple-600 text-purple-600'
                                                    : 'bg-gray-100 border-gray-300 text-gray-400'
                                            }`}
                                        >
                                            {isCompleted ? <Check className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                                        </div>
                                        <p className={`mt-2 text-xs font-semibold ${isCurrent ? 'text-purple-600' : 'text-gray-500'}`}>
                                            {step.title}
                                        </p>
                                    </div>
                                    {index < STEPS.length - 1 && (
                                        <div
                                            className={`h-0.5 flex-1 mx-2 ${
                                                isCompleted ? 'bg-purple-600' : 'bg-gray-300'
                                            }`}
                                        />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Step Content */}
                <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-200 p-8 mb-6">
                    {currentStep === 1 && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-black">Información de tu empresa</h2>
                            <p className="text-gray-600">
                                Esta información nos ayudará a personalizar tu experiencia
                            </p>

                            <div>
                                <label className="block text-sm font-bold text-black mb-2">
                                    Nombre de la empresa
                                </label>
                                <Input
                                    name="company_name"
                                    value={formData.company_name}
                                    onChange={handleChange}
                                    placeholder="Mi Empresa S.A."
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-black mb-2">
                                    Teléfono de contacto
                                </label>
                                <Input
                                    name="phone"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    placeholder="+52 55 1234 5678"
                                    required
                                />
                            </div>
                        </div>
                    )}

                    {currentStep === 2 && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-black">Configuración regional</h2>
                            <p className="text-gray-600">
                                Ajusta tu zona horaria e idioma preferido
                            </p>

                            <div>
                                <label className="block text-sm font-bold text-black mb-2">
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

                            <div>
                                <label className="block text-sm font-bold text-black mb-2">
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
                        </div>
                    )}

                    {currentStep === 3 && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-black">Selecciona tu plan</h2>
                            <p className="text-gray-600">
                                Comienza con nuestro plan gratuito o elige uno de nuestros planes premium
                            </p>

                            <div className="grid md:grid-cols-3 gap-4">
                                <div className="border-2 border-gray-300 rounded-lg p-6 hover:border-purple-600 transition cursor-pointer">
                                    <h3 className="text-lg font-bold mb-2">Starter</h3>
                                    <p className="text-3xl font-black mb-4">$0<span className="text-sm text-gray-500">/mes</span></p>
                                    <ul className="space-y-2 text-sm text-gray-600">
                                        <li>✓ 100 mensajes/mes</li>
                                        <li>✓ 1 bot</li>
                                        <li>✓ Soporte por email</li>
                                    </ul>
                                    <Button className="w-full mt-4" variant="outline">
                                        Plan actual
                                    </Button>
                                </div>

                                <div className="border-2 border-purple-600 rounded-lg p-6 relative bg-purple-50">
                                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                                        Recomendado
                                    </div>
                                    <h3 className="text-lg font-bold mb-2">Professional</h3>
                                    <p className="text-3xl font-black mb-4">$49<span className="text-sm text-gray-500">/mes</span></p>
                                    <ul className="space-y-2 text-sm text-gray-600">
                                        <li>✓ 5,000 mensajes/mes</li>
                                        <li>✓ 3 bots</li>
                                        <li>✓ Integraciones HubSpot/Twilio</li>
                                        <li>✓ Soporte prioritario</li>
                                    </ul>
                                    <Button className="w-full mt-4">
                                        Elegir plan
                                    </Button>
                                </div>

                                <div className="border-2 border-gray-300 rounded-lg p-6 hover:border-purple-600 transition cursor-pointer">
                                    <h3 className="text-lg font-bold mb-2">Enterprise</h3>
                                    <p className="text-3xl font-black mb-4">$199<span className="text-sm text-gray-500">/mes</span></p>
                                    <ul className="space-y-2 text-sm text-gray-600">
                                        <li>✓ Mensajes ilimitados</li>
                                        <li>✓ Bots ilimitados</li>
                                        <li>✓ Todas las integraciones</li>
                                        <li>✓ Soporte 24/7</li>
                                    </ul>
                                    <Button className="w-full mt-4" variant="outline">
                                        Contactar ventas
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}

                    {currentStep === 4 && (
                        <div className="text-center space-y-6 py-8">
                            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                                <Check className="w-12 h-12 text-green-600" />
                            </div>
                            <h2 className="text-3xl font-bold text-black">¡Todo listo!</h2>
                            <p className="text-gray-600 max-w-md mx-auto">
                                Tu cuenta ha sido configurada exitosamente. Estás listo para comenzar a automatizar tus ventas con WhatsApp.
                            </p>
                            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 max-w-md mx-auto">
                                <h3 className="font-bold text-purple-900 mb-2">Próximos pasos recomendados:</h3>
                                <ul className="text-sm text-purple-800 space-y-2 text-left">
                                    <li>→ Conecta tu cuenta de Twilio para WhatsApp</li>
                                    <li>→ Sincroniza con HubSpot CRM (opcional)</li>
                                    <li>→ Configura tu primer bot de ventas</li>
                                    <li>→ Sube documentos para RAG</li>
                                </ul>
                            </div>
                        </div>
                    )}
                </div>

                {/* Navigation Buttons */}
                <div className="flex justify-between">
                    <Button
                        variant="outline"
                        onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                        disabled={currentStep === 1 || loading}
                    >
                        Anterior
                    </Button>

                    {currentStep < 4 ? (
                        <Button onClick={handleNext} disabled={loading}>
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <LoadingSpinner size="sm" variant="default" />
                                    Guardando...
                                </span>
                            ) : (
                                <span className="flex items-center gap-2">
                                    Siguiente
                                    <ChevronRight className="w-4 h-4" />
                                </span>
                            )}
                        </Button>
                    ) : (
                        <Button onClick={handleFinish} disabled={loading}>
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <LoadingSpinner size="sm" variant="default" />
                                    Finalizando...
                                </span>
                            ) : (
                                'Ir al Dashboard'
                            )}
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}

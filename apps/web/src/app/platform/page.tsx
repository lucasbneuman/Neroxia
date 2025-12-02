'use client';

import { MainNav } from '@/components/ui/MainNav';
import Link from 'next/link';

export default function PlatformPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-[#0f0f0f]">
            <MainNav />

            <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-5xl sm:text-6xl font-black text-center mb-6 text-gray-900 dark:text-white">
                        La <span className="bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] bg-clip-text text-transparent">Plataforma</span> más Poderosa
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-400 text-center mb-16 font-bold max-w-3xl mx-auto">
                        Todo lo que necesitas para automatizar y escalar tus ventas en WhatsApp
                    </p>

                    {/* Dashboard Preview */}
                    <div className="mb-20">
                        <div className="bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] p-1 rounded-2xl shadow-accent">
                            <div className="bg-white dark:bg-[#0f0f0f] rounded-xl p-8">
                                <div className="aspect-video bg-gray-100 dark:bg-[#18181b] rounded-xl flex items-center justify-center border border-gray-200 dark:border-[#27272a]">
                                    <div className="text-center">
                                        <div className="w-20 h-20 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mx-auto mb-4 shadow-accent">
                                            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                            </svg>
                                        </div>
                                        <p className="text-gray-600 dark:text-gray-400 font-black text-lg">Dashboard Preview</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Platform Features */}
                    <div className="grid md:grid-cols-2 gap-12 mb-20">
                        <div>
                            <div className="w-16 h-16 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 shadow-accent">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                            </div>
                            <h2 className="text-3xl font-black mb-4 text-gray-900 dark:text-white">
                                Gestión de Conversaciones
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed mb-4">
                                Visualiza y gestiona todas tus conversaciones de WhatsApp en tiempo real. Interviene manualmente cuando lo necesites o deja que la IA haga el trabajo.
                            </p>
                            <ul className="space-y-3">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Vista unificada de todos los chats</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Modo manual para intervención humana</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Historial completo de mensajes</span>
                                </li>
                            </ul>
                        </div>

                        <div>
                            <div className="w-16 h-16 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 shadow-accent">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <h2 className="text-3xl font-black mb-4 text-gray-900 dark:text-white">
                                Configuración Inteligente
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed mb-4">
                                Personaliza completamente el comportamiento de tu agente de IA. Define respuestas, productos, precios y flujos de conversación.
                            </p>
                            <ul className="space-y-3">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Editor de prompts y respuestas</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Base de conocimiento personalizada</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Configuración de productos y precios</span>
                                </li>
                            </ul>
                        </div>

                        <div>
                            <div className="w-16 h-16 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 shadow-accent">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <h2 className="text-3xl font-black mb-4 text-gray-900 dark:text-white">
                                CRM Integrado
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed mb-4">
                                Gestiona todos tus contactos, leads y deals en un solo lugar. Sincronización automática con HubSpot y otros CRMs populares.
                            </p>
                            <ul className="space-y-3">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Gestión de contactos y deals</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Notas y etiquetas personalizadas</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Integración con HubSpot</span>
                                </li>
                            </ul>
                        </div>

                        <div>
                            <div className="w-16 h-16 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 shadow-accent">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                </svg>
                            </div>
                            <h2 className="text-3xl font-black mb-4 text-gray-900 dark:text-white">
                                Testing y Optimización
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed mb-4">
                                Prueba tu agente de IA antes de ponerlo en producción. Optimiza las respuestas y flujos para maximizar conversiones.
                            </p>
                            <ul className="space-y-3">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Simulador de conversaciones</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Análisis de rendimiento</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">A/B testing de respuestas</span>
                                </li>
                            </ul>
                        </div>
                    </div>

                    {/* CTA */}
                    <div className="text-center bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] p-12 rounded-2xl shadow-accent">
                        <h2 className="text-4xl font-black mb-4 text-white">
                            Listo para Probar la Plataforma?
                        </h2>
                        <p className="text-xl text-white/90 mb-8 font-bold">
                            Comienza gratis y descubre todo lo que Oracle Sales puede hacer por tu negocio
                        </p>
                        <Link
                            href="/login"
                            className="inline-block px-10 py-4 bg-white text-[#8B5CF6] font-black text-lg rounded-xl shadow-lg hover:shadow-2xl hover:scale-105 transition-all"
                        >
                            Comenzar Ahora
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}

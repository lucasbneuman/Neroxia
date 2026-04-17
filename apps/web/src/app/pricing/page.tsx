'use client';

import { MainNav } from '@/components/ui/MainNav';
import Link from 'next/link';

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-[#0f0f0f]">
            <MainNav />

            <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-5xl sm:text-6xl font-black text-center mb-6 text-gray-900 dark:text-white">
                        Planes y <span className="bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] bg-clip-text text-transparent">Precios</span>
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-400 text-center mb-16 font-bold max-w-3xl mx-auto">
                        Elige el plan perfecto para tu negocio. Todos incluyen acceso completo a nuestra IA de ventas.
                    </p>

                    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {/* Starter Plan */}
                        <div className="bg-white dark:bg-[#18181b] p-8 rounded-2xl shadow-medium border border-gray-200 dark:border-[#27272a] hover:shadow-large transition-all">
                            <h3 className="text-2xl font-black mb-2 text-gray-900 dark:text-white">Starter</h3>
                            <div className="mb-6">
                                <span className="text-5xl font-black text-gray-900 dark:text-white">$49</span>
                                <span className="text-gray-600 dark:text-gray-400 font-bold">/mes</span>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Hasta 1,000 conversaciones/mes</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">1 número de WhatsApp</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">CRM básico</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Soporte por email</span>
                                </li>
                            </ul>
                            <Link
                                href="/login"
                                className="block w-full text-center px-6 py-3 bg-gray-100 dark:bg-[#27272a] text-gray-900 dark:text-white font-black rounded-xl hover:bg-gray-200 dark:hover:bg-[#3f3f46] transition-all"
                            >
                                Comenzar
                            </Link>
                        </div>

                        {/* Professional Plan - Featured */}
                        <div className="bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] p-8 rounded-2xl shadow-accent scale-105 relative">
                            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-[#0f0f0f] px-4 py-1 rounded-full">
                                <span className="text-[#8B5CF6] font-black text-sm">MÁS POPULAR</span>
                            </div>
                            <h3 className="text-2xl font-black mb-2 text-white">Professional</h3>
                            <div className="mb-6">
                                <span className="text-5xl font-black text-white">$149</span>
                                <span className="text-white/80 font-bold">/mes</span>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-white mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-white font-bold">Hasta 5,000 conversaciones/mes</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-white mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-white font-bold">3 números de WhatsApp</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-white mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-white font-bold">CRM avanzado + Analytics</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-white mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-white font-bold">Integraciones API</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-white mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-white font-bold">Soporte prioritario</span>
                                </li>
                            </ul>
                            <Link
                                href="/login"
                                className="block w-full text-center px-6 py-3 bg-white text-[#8B5CF6] font-black rounded-xl hover:shadow-lg hover:scale-105 transition-all"
                            >
                                Comenzar
                            </Link>
                        </div>

                        {/* Enterprise Plan */}
                        <div className="bg-white dark:bg-[#18181b] p-8 rounded-2xl shadow-medium border border-gray-200 dark:border-[#27272a] hover:shadow-large transition-all">
                            <h3 className="text-2xl font-black mb-2 text-gray-900 dark:text-white">Enterprise</h3>
                            <div className="mb-6">
                                <span className="text-5xl font-black text-gray-900 dark:text-white">Custom</span>
                            </div>
                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Conversaciones ilimitadas</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Números ilimitados</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Personalización completa</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">Account manager dedicado</span>
                                </li>
                                <li className="flex items-start">
                                    <svg className="w-6 h-6 text-[#8B5CF6] mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-gray-600 dark:text-gray-400 font-bold">SLA garantizado</span>
                                </li>
                            </ul>
                            <Link
                                href="/login"
                                className="block w-full text-center px-6 py-3 bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] text-white font-black rounded-xl hover:shadow-accent hover:scale-105 transition-all"
                            >
                                Contactar Ventas
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

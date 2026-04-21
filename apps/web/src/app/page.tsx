'use client';

import { MainNav } from '@/components/ui/MainNav';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-[#0f0f0f]">
      <MainNav />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black mb-6 leading-tight">
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] bg-clip-text text-transparent">
              Neroxia
            </span>
            <br />
            <span className="text-gray-900 dark:text-white">
              Tu Agente de IA para WhatsApp
            </span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-10 max-w-3xl mx-auto font-bold">
            Automatiza tus ventas con inteligencia artificial. Atiende clientes 24/7,
            califica leads y cierra más negocios sin esfuerzo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/login"
              className="px-8 py-4 bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] text-white font-black text-lg rounded-xl shadow-accent hover:shadow-lg hover:scale-105 transition-all"
            >
              Comenzar Gratis
            </Link>
            <Link
              href="/platform"
              className="px-8 py-4 bg-white dark:bg-[#18181b] text-gray-900 dark:text-white font-black text-lg rounded-xl border-2 border-gray-200 dark:border-[#27272a] hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6] transition-all"
            >
              Ver Plataforma
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-[#18181b]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl sm:text-5xl font-black text-center mb-4 text-gray-900 dark:text-white">
            Potencia tus Ventas con IA
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 text-center mb-16 font-bold">
            Neroxia revoluciona tu proceso de ventas en WhatsApp
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Conversaciones Inteligentes
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                IA avanzada que mantiene conversaciones naturales, responde preguntas y guía a tus clientes hacia la compra.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Integración WhatsApp
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                Conecta directamente con WhatsApp Business. Tus clientes chatean donde ya están, sin apps adicionales.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Calificación Automática
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                Identifica y prioriza los mejores leads automáticamente. Enfoca tu equipo en las oportunidades más valiosas.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Disponibilidad 24/7
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                Nunca pierdas una venta. Neroxia atiende a tus clientes en cualquier momento, día y noche.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                CRM Integrado
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                Gestiona todos tus contactos, conversaciones y deals en un solo lugar. Sincronización automática con tu CRM.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-white dark:bg-[#0f0f0f] p-8 rounded-2xl shadow-medium hover:shadow-large transition-all border border-gray-100 dark:border-[#27272a] group hover:border-[#8B5CF6] dark:hover:border-[#8B5CF6]">
              <div className="w-14 h-14 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-accent">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Multi-idioma
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold leading-relaxed">
                Atiende clientes en su idioma preferido. Neroxia se adapta automáticamente a cada conversación.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl sm:text-5xl font-black text-center mb-4 text-gray-900 dark:text-white">
            Cómo Funciona
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 text-center mb-16 font-bold">
            Empieza a vender en minutos
          </p>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-full flex items-center justify-center mx-auto mb-6 shadow-accent">
                <span className="text-white font-black text-3xl">1</span>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Conecta WhatsApp
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold">
                Vincula tu número de WhatsApp Business en segundos con nuestro asistente de configuración.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-full flex items-center justify-center mx-auto mb-6 shadow-accent">
                <span className="text-white font-black text-3xl">2</span>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Configura tu Agente
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold">
                Personaliza las respuestas, productos y flujos de venta según tu negocio.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] rounded-full flex items-center justify-center mx-auto mb-6 shadow-accent">
                <span className="text-white font-black text-3xl">3</span>
              </div>
              <h3 className="text-2xl font-black mb-3 text-gray-900 dark:text-white">
                Vende Automáticamente
              </h3>
              <p className="text-gray-600 dark:text-gray-400 font-bold">
                Neroxia empieza a atender clientes, calificar leads y cerrar ventas por ti.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl sm:text-5xl font-black mb-6 text-white">
            Listo para Transformar tus Ventas?
          </h2>
          <p className="text-xl text-white/90 mb-10 font-bold">
            Únete a cientos de empresas que ya están vendiendo más con Neroxia
          </p>
          <Link
            href="/login"
            className="inline-block px-10 py-5 bg-white text-[#8B5CF6] font-black text-xl rounded-xl shadow-lg hover:shadow-2xl hover:scale-105 transition-all"
          >
            Comenzar Ahora - Es Gratis
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-[#18181b] border-t border-gray-200 dark:border-[#27272a]">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] flex items-center justify-center shadow-accent">
              <span className="text-white font-black text-xl">N</span>
            </div>
            <span className="text-xl font-black bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] bg-clip-text text-transparent">
              Neroxia
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 font-bold">
            © 2025 Neroxia. Todos los derechos reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}

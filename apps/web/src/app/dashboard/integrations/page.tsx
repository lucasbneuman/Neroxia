'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { getHubSpotStatus, getTwilioStatus } from '@/lib/api';
import { CheckCircle2, XCircle, ExternalLink, Copy, Phone, Users } from 'lucide-react';

export default function IntegrationsPage() {
    const { addToast } = useToast();
    const [loading, setLoading] = useState(true);
    const [hubspotConnected, setHubspotConnected] = useState(false);
    const [twilioConnected, setTwilioConnected] = useState(false);

    useEffect(() => {
        loadStatus();
    }, []);

    const loadStatus = async () => {
        try {
            const [hubspot, twilio] = await Promise.all([
                getHubSpotStatus().catch(() => ({ status: 'disconnected' })),
                getTwilioStatus().catch(() => ({ status: 'disconnected' })),
            ]);

            setHubspotConnected(hubspot.status === 'active');
            setTwilioConnected(twilio.status === 'active');
        } catch (error) {
            console.error('Error loading integration status:', error);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        addToast('Copiado al portapapeles', 'success');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    const webhookUrl = typeof window !== 'undefined'
        ? `${window.location.origin}/webhook/twilio`
        : 'https://tu-dominio.com/webhook/twilio';

    return (
        <div className="max-w-5xl mx-auto p-6">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-black dark:text-white">Integraciones</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Conecta tus servicios favoritos para potenciar tu bot de ventas
                </p>
            </div>

            <div className="space-y-6">
                {/* Twilio Integration */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                                <Phone className="w-6 h-6 text-red-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-black dark:text-white">Twilio WhatsApp</h2>
                                <p className="text-sm text-gray-600">Conecta tu número de WhatsApp Business</p>
                            </div>
                        </div>
                        {twilioConnected ? (
                            <div className="flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <CheckCircle2 className="w-4 h-4" />
                                Conectado
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <XCircle className="w-4 h-4" />
                                No conectado
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        <p className="text-gray-700 dark:text-gray-300">
                            Twilio permite que tu bot reciba y envíe mensajes por WhatsApp. Sigue estos pasos para configurar la integración:
                        </p>

                        <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
                            <h3 className="font-bold text-purple-900 mb-3">Pasos de configuración:</h3>
                            <ol className="space-y-3 text-sm text-purple-800">
                                <li className="flex gap-2">
                                    <span className="font-bold">1.</span>
                                    <div>
                                        <span>Crea una cuenta en Twilio y obtén un número de WhatsApp Business: </span>
                                        <a
                                            href="https://www.twilio.com/console"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-purple-600 hover:underline inline-flex items-center gap-1"
                                        >
                                            Ir a Twilio Console
                                            <ExternalLink className="w-3 h-3" />
                                        </a>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="font-bold">2.</span>
                                    <span>Copia tus credenciales (Account SID, Auth Token, WhatsApp Number)</span>
                                </li>
                                <li className="flex gap-2">
                                    <span className="font-bold">3.</span>
                                    <span>Agrega estas variables a tu archivo .env en el servidor:</span>
                                </li>
                            </ol>

                            <div className="mt-3 bg-gray-900 text-white p-3 rounded-lg font-mono text-xs">
                                <div>TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx</div>
                                <div>TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</div>
                                <div>TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886</div>
                            </div>

                            <div className="mt-3 space-y-2">
                                <p className="font-bold">4. Configura el Webhook en Twilio:</p>
                                <p>En la configuración de tu número de WhatsApp en Twilio, establece el webhook:</p>
                                <div className="flex items-center gap-2 bg-white border border-purple-300 rounded-lg p-2">
                                    <code className="flex-1 text-xs">{webhookUrl}</code>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => copyToClipboard(webhookUrl)}
                                        className="shrink-0"
                                    >
                                        <Copy className="w-3 h-3 mr-1" />
                                        Copiar
                                    </Button>
                                </div>
                                <p className="text-xs">Método HTTP: <strong>POST</strong></p>
                            </div>

                            <div className="mt-3">
                                <p className="font-bold">5. Reinicia el servidor API para aplicar los cambios</p>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <Button variant="outline" asChild>
                                <a
                                    href="https://www.twilio.com/docs/whatsapp/quickstart"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <ExternalLink className="w-4 h-4 mr-2" />
                                    Ver documentación de Twilio
                                </a>
                            </Button>
                        </div>
                    </div>
                </div>

                {/* HubSpot Integration */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                                <Users className="w-6 h-6 text-orange-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-black dark:text-white">HubSpot CRM</h2>
                                <p className="text-sm text-gray-600">Sincroniza contactos y deals automáticamente</p>
                            </div>
                        </div>
                        {hubspotConnected ? (
                            <div className="flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <CheckCircle2 className="w-4 h-4" />
                                Conectado
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <XCircle className="w-4 h-4" />
                                No conectado
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        <p className="text-gray-700 dark:text-gray-300">
                            HubSpot te permite sincronizar automáticamente todos los contactos y leads capturados por el bot con tu CRM.
                        </p>

                        <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
                            <h3 className="font-bold text-purple-900 mb-3">Pasos de configuración:</h3>
                            <ol className="space-y-3 text-sm text-purple-800">
                                <li className="flex gap-2">
                                    <span className="font-bold">1.</span>
                                    <div>
                                        <span>Accede a tu cuenta de HubSpot: </span>
                                        <a
                                            href="https://app.hubspot.com"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-purple-600 hover:underline inline-flex items-center gap-1"
                                        >
                                            Ir a HubSpot
                                            <ExternalLink className="w-3 h-3" />
                                        </a>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="font-bold">2.</span>
                                    <span>Ve a Settings → Integrations → Private Apps</span>
                                </li>
                                <li className="flex gap-2">
                                    <span className="font-bold">3.</span>
                                    <span>Crea una Private App con los siguientes permisos:</span>
                                </li>
                            </ol>

                            <div className="mt-3 bg-white border border-purple-300 rounded-lg p-3">
                                <ul className="space-y-1 text-xs text-purple-900">
                                    <li>✓ <strong>crm.objects.contacts</strong> (Read & Write)</li>
                                    <li>✓ <strong>crm.objects.deals</strong> (Read & Write)</li>
                                    <li>✓ <strong>crm.schemas.contacts</strong> (Read & Write)</li>
                                    <li>✓ <strong>crm.schemas.deals</strong> (Read & Write)</li>
                                </ul>
                            </div>

                            <div className="mt-3 space-y-2">
                                <p className="font-bold">4. Genera tu Access Token</p>
                                <p>Copia el token generado y agrégalo a tu archivo .env:</p>
                                <div className="bg-gray-900 text-white p-3 rounded-lg font-mono text-xs">
                                    <div>HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</div>
                                </div>
                            </div>

                            <div className="mt-3">
                                <p className="font-bold">5. Reinicia el servidor API para aplicar los cambios</p>
                            </div>

                            <div className="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
                                <h4 className="font-bold text-green-900 mb-2">¿Qué se sincroniza automáticamente?</h4>
                                <ul className="space-y-1 text-xs text-green-800">
                                    <li>✓ Contactos con nombre, email, teléfono</li>
                                    <li>✓ Intent Score (puntuación de intención de compra)</li>
                                    <li>✓ Sentiment (sentimiento del cliente)</li>
                                    <li>✓ Needs & Pain Points (necesidades identificadas)</li>
                                    <li>✓ Budget (presupuesto mencionado)</li>
                                    <li>✓ Lifecycle Stage (etapa del cliente)</li>
                                    <li>✓ Notas de conversación automáticas</li>
                                </ul>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <Button variant="outline" asChild>
                                <a
                                    href="https://developers.hubspot.com/docs/api/private-apps"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <ExternalLink className="w-4 h-4 mr-2" />
                                    Ver documentación de HubSpot
                                </a>
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Info Panel */}
                <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                    <h3 className="font-bold text-blue-900 mb-2">💡 Nota importante</h3>
                    <p className="text-sm text-blue-800">
                        Las variables de entorno (TWILIO_*, HUBSPOT_*) deben configurarse en el servidor donde está
                        desplegada la API. Si estás usando Render, Docker u otra plataforma, asegúrate de agregar
                        estas variables en la configuración de tu servicio.
                    </p>
                </div>
            </div>
        </div>
    );
}

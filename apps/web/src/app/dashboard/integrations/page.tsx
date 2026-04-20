'use client';

import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import { getHubSpotStatus, getTwilioStatus, getWebWidgetConfig, regenerateWebWidgetCredentials, updateWebWidgetConfig } from '@/lib/api';
import type { WebWidgetConfig } from '@/types';
import { CheckCircle2, XCircle, ExternalLink, Copy, Phone, Users, Instagram, Facebook, AlertCircle, Globe, RefreshCw } from 'lucide-react';

interface ChannelIntegration {
    channel: 'instagram' | 'messenger';
    connected: boolean;
    page_name?: string;
    page_id?: string;
}

export default function IntegrationsPage() {
    const { addToast } = useToast();
    const [loading, setLoading] = useState(true);
    const [hubspotConnected, setHubspotConnected] = useState(false);
    const [twilioConnected, setTwilioConnected] = useState(false);
    const [channelIntegrations, setChannelIntegrations] = useState<ChannelIntegration[]>([]);
    const [webWidgetConfig, setWebWidgetConfig] = useState<WebWidgetConfig | null>(null);
    const [allowedOriginsInput, setAllowedOriginsInput] = useState('');
    const [primaryColorInput, setPrimaryColorInput] = useState('#7C3AED');
    const [savingWidget, setSavingWidget] = useState(false);
    const [regeneratingWidget, setRegeneratingWidget] = useState(false);

    const loadStatus = useCallback(async () => {
        setLoading(true);
        try {
            const [hubspot, twilio, channels, widget] = await Promise.all([
                getHubSpotStatus().catch(() => ({ status: 'disconnected' })),
                getTwilioStatus().catch(() => ({ status: 'disconnected' })),
                fetch('/api/integrations/list', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                }).then(res => res.json()).catch(() => [] as ChannelIntegration[]),
                getWebWidgetConfig().catch(() => null)
            ]);

            setHubspotConnected(hubspot.status === 'active');
            setTwilioConnected(twilio.status === 'active');
            setChannelIntegrations(channels);
            if (widget) {
                setWebWidgetConfig(widget);
                setAllowedOriginsInput(widget.allowed_origins.join('\n'));
                setPrimaryColorInput(widget.default_primary_color);
            }
        } catch (error) {
            console.error('Error loading integration status:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    const checkOAuthCallback = useCallback(() => {
        const params = new URLSearchParams(window.location.search);
        const status = params.get('status');

        if (status === 'success') {
            addToast('¡Cuenta conectada exitosamente!', 'success');
            window.history.replaceState({}, '', '/dashboard/integrations');
            loadStatus();
        } else if (status === 'error') {
            addToast('Error al conectar la cuenta', 'error');
            window.history.replaceState({}, '', '/dashboard/integrations');
        }
    }, [addToast, loadStatus]);

    useEffect(() => {
        void loadStatus();
        checkOAuthCallback();
    }, [checkOAuthCallback, loadStatus]);

    const connectChannel = async (channel: 'instagram' | 'messenger') => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const token = localStorage.getItem('token');

            const response = await fetch(`${API_URL}/integrations/facebook/connect?channel=${channel}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!response.ok) {
                throw new Error('Failed to initiate OAuth');
            }

            const data = await response.json();
            window.location.href = data.oauth_url;
        } catch {
            addToast('Error al iniciar la conexión', 'error');
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        addToast('Copiado al portapapeles', 'success');
    };

    const refreshWebWidget = async () => {
        const config = await getWebWidgetConfig();
        setWebWidgetConfig(config);
        setAllowedOriginsInput(config.allowed_origins.join('\n'));
        setPrimaryColorInput(config.default_primary_color);
    };

    const saveWebWidgetConfig = async () => {
        try {
            setSavingWidget(true);
            const config = await updateWebWidgetConfig({
                enabled: true,
                allowed_origins: allowedOriginsInput.split('\n').map((value) => value.trim()).filter(Boolean),
                default_primary_color: primaryColorInput,
            });
            setWebWidgetConfig(config);
            addToast('Widget web actualizado', 'success');
        } catch {
            addToast('No se pudo guardar el widget web', 'error');
        } finally {
            setSavingWidget(false);
        }
    };

    const handleRegenerateWidget = async () => {
        try {
            setRegeneratingWidget(true);
            const config = await regenerateWebWidgetCredentials();
            setWebWidgetConfig(config);
            setAllowedOriginsInput(config.allowed_origins.join('\n'));
            setPrimaryColorInput(config.default_primary_color);
            addToast('Credenciales del widget regeneradas', 'success');
        } catch {
            addToast('No se pudieron regenerar las credenciales', 'error');
        } finally {
            setRegeneratingWidget(false);
        }
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
                {/* Instagram Integration */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                                <Instagram className="w-6 h-6 text-pink-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-black dark:text-white">Instagram Direct</h2>
                                <p className="text-sm text-gray-600">Recibe y responde a mensajes directos automáticamente</p>
                            </div>
                        </div>
                        {channelIntegrations.find(i => i.channel === 'instagram')?.connected ? (
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
                            Conecta tu cuenta de Instagram Business para gestionar mensajes directos automáticamente con tu bot de ventas.
                        </p>

                        {channelIntegrations.find(i => i.channel === 'instagram')?.connected ? (
                            <div className="space-y-4">
                                <div>
                                    <p className="text-sm text-gray-500">Página conectada:</p>
                                    <p className="font-medium text-black dark:text-white">
                                        {channelIntegrations.find(i => i.channel === 'instagram')?.page_name}
                                    </p>
                                </div>
                                <Button variant="outline" className="w-full" disabled>
                                    Desconectar
                                </Button>
                            </div>
                        ) : (
                            <Button
                                onClick={() => connectChannel('instagram')}
                                className="w-full bg-pink-500 hover:bg-pink-600 text-white"
                            >
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Conectar Instagram
                            </Button>
                        )}
                    </div>
                </div>

                {/* Messenger Integration */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Facebook className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-black dark:text-white">Facebook Messenger</h2>
                                <p className="text-sm text-gray-600">Recibe y responde a mensajes de Messenger automáticamente</p>
                            </div>
                        </div>
                        {channelIntegrations.find(i => i.channel === 'messenger')?.connected ? (
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
                            Conecta tu página de Facebook para responder automáticamente a mensajes de Messenger con tu bot.
                        </p>

                        {channelIntegrations.find(i => i.channel === 'messenger')?.connected ? (
                            <div className="space-y-4">
                                <div>
                                    <p className="text-sm text-gray-500">Página conectada:</p>
                                    <p className="font-medium text-black dark:text-white">
                                        {channelIntegrations.find(i => i.channel === 'messenger')?.page_name}
                                    </p>
                                </div>
                                <Button variant="outline" className="w-full" disabled>
                                    Desconectar
                                </Button>
                            </div>
                        ) : (
                            <Button
                                onClick={() => connectChannel('messenger')}
                                className="w-full bg-blue-500 hover:bg-blue-600 text-white"
                            >
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Conectar Messenger
                            </Button>
                        )}
                    </div>
                </div>

                {/* Setup Instructions */}
                <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-purple-600 mt-0.5 shrink-0" />
                        <div>
                            <h3 className="font-bold text-purple-900 mb-2">Cómo conectar Instagram/Messenger</h3>
                            <ol className="space-y-2 text-sm text-purple-800">
                                <li>1. Haz clic en &quot;Conectar Instagram&quot; o &quot;Conectar Messenger&quot;</li>
                                <li>2. Inicia sesión en Facebook</li>
                                <li>3. Selecciona la página que deseas conectar</li>
                                <li>4. Acepta los permisos solicitados</li>
                                <li>5. Serás redirigido de vuelta aquí</li>
                                <li>6. ¡Comienza a recibir mensajes automáticamente!</li>
                            </ol>
                        </div>
                    </div>
                </div>

                {/* Web Widget Integration */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
                                <Globe className="w-6 h-6 text-amber-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-black dark:text-white">Web Widget</h2>
                                <p className="text-sm text-gray-600">Inserta tu chatbot en cualquier sitio o app web con un snippet.</p>
                            </div>
                        </div>
                        {webWidgetConfig?.enabled ? (
                            <div className="flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <CheckCircle2 className="w-4 h-4" />
                                Activo
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-semibold">
                                <XCircle className="w-4 h-4" />
                                Inactivo
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        <p className="text-gray-700 dark:text-gray-300">
                            El widget abre un chat flotante en la esquina inferior derecha, usa la configuración principal del bot y registra las conversaciones como canal web dentro del dashboard.
                        </p>

                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-semibold text-gray-900 dark:text-white">Dominios permitidos</label>
                                <textarea
                                    value={allowedOriginsInput}
                                    onChange={(event) => setAllowedOriginsInput(event.target.value)}
                                    className="w-full min-h-36 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                                    placeholder={'https://mi-sitio.com\nhttps://app.mi-sitio.com'}
                                />
                                <p className="text-xs text-gray-500">Uno por línea. El widget sólo responderá desde estos orígenes.</p>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">Color principal</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={primaryColorInput}
                                            onChange={(event) => setPrimaryColorInput(event.target.value)}
                                            className="h-11 w-14 rounded border border-gray-300 bg-white"
                                        />
                                        <input
                                            type="text"
                                            value={primaryColorInput}
                                            onChange={(event) => setPrimaryColorInput(event.target.value)}
                                            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                                        />
                                    </div>
                                </div>

                                <div className="rounded-2xl border border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900">
                                    <p className="text-xs text-gray-500 mb-3">Preview rápido</p>
                                    <div className="flex items-center justify-between rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-4 py-3">
                                        <div>
                                            <p className="font-semibold text-sm text-black dark:text-white">Asistente Web</p>
                                            <p className="text-xs text-gray-500">Ventana flotante embebida</p>
                                        </div>
                                        <div
                                            className="h-11 w-11 rounded-full shadow-lg"
                                            style={{ backgroundColor: primaryColorInput }}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <p className="text-sm font-semibold text-gray-900 dark:text-white">Widget ID</p>
                                    <div className="flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2 bg-gray-50 dark:bg-gray-900">
                                        <code className="flex-1 text-xs">{webWidgetConfig?.widget_id || 'Generando...'}</code>
                                        {webWidgetConfig?.widget_id && (
                                            <Button size="sm" variant="outline" onClick={() => copyToClipboard(webWidgetConfig.widget_id)}>
                                                <Copy className="w-3 h-3 mr-1" />
                                                Copiar
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between gap-3">
                                <p className="text-sm font-semibold text-gray-900 dark:text-white">Snippet para pegar en tu sitio</p>
                                {webWidgetConfig?.snippet && (
                                    <Button variant="outline" onClick={() => copyToClipboard(webWidgetConfig.snippet)}>
                                        <Copy className="w-4 h-4 mr-2" />
                                        Copiar snippet
                                    </Button>
                                )}
                            </div>
                            <pre className="overflow-x-auto rounded-lg bg-gray-950 text-gray-100 p-4 text-xs">
                                <code>{webWidgetConfig?.snippet || 'Cargando snippet...'}</code>
                            </pre>
                        </div>

                        <div className="flex flex-wrap gap-2">
                            <Button onClick={saveWebWidgetConfig} disabled={savingWidget}>
                                {savingWidget ? 'Guardando...' : 'Guardar Widget'}
                            </Button>
                            <Button variant="outline" onClick={handleRegenerateWidget} disabled={regeneratingWidget}>
                                <RefreshCw className="w-4 h-4 mr-2" />
                                {regeneratingWidget ? 'Regenerando...' : 'Regenerar credenciales'}
                            </Button>
                            <Button variant="outline" onClick={() => void refreshWebWidget()}>
                                Actualizar
                            </Button>
                        </div>
                    </div>
                </div>

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
                            <a
                                href="https://www.twilio.com/docs/whatsapp/quickstart"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex"
                            >
                                <Button variant="outline">
                                    <ExternalLink className="w-4 h-4 mr-2" />
                                    Ver documentación de Twilio
                                </Button>
                            </a>
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
                            <a
                                href="https://developers.hubspot.com/docs/api/private-apps"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex"
                            >
                                <Button variant="outline">
                                    <ExternalLink className="w-4 h-4 mr-2" />
                                    Ver documentación de HubSpot
                                </Button>
                            </a>
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

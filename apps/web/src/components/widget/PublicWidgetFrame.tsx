'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

type WidgetMessage = {
    id?: number;
    message_text: string;
    sender: 'user' | 'bot';
    created_at?: string | null;
};

interface PublicWidgetFrameProps {
    widgetId: string;
    primaryColor: string;
    apiBase: string;
    hostPageUrl: string;
}

export function PublicWidgetFrame({
    widgetId,
    primaryColor,
    apiBase,
    hostPageUrl,
}: PublicWidgetFrameProps) {
    const storageKey = useMemo(() => `wa-sales-widget:${widgetId}:session`, [widgetId]);
    const [messages, setMessages] = useState<WidgetMessage[]>([]);
    const [sessionToken, setSessionToken] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!widgetId) {
            setError('Widget ID inválido');
            setLoading(false);
            return;
        }

        const bootstrap = async () => {
            try {
                setLoading(true);
                setError(null);
                const storedSessionId = typeof window !== 'undefined' ? localStorage.getItem(storageKey) : null;
                const resolvedOrigin = hostPageUrl ? new URL(hostPageUrl).origin : (document.referrer ? new URL(document.referrer).origin : window.location.origin);
                const resolvedPageUrl = hostPageUrl || document.referrer || window.location.href;
                const response = await fetch(`${apiBase}/widget/bootstrap`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        widget_id: widgetId,
                        origin: resolvedOrigin,
                        page_url: resolvedPageUrl,
                        session_id: storedSessionId || undefined,
                    }),
                });

                if (!response.ok) {
                    throw new Error('No se pudo iniciar el widget');
                }

                const data = await response.json();
                setSessionToken(data.token);
                setSessionId(data.session_id);
                setMessages(data.conversation?.messages || []);
                if (typeof window !== 'undefined') {
                    localStorage.setItem(storageKey, data.session_id);
                }
            } catch (bootstrapError) {
                setError(bootstrapError instanceof Error ? bootstrapError.message : 'Error al iniciar el widget');
            } finally {
                setLoading(false);
            }
        };

        void bootstrap();
    }, [apiBase, hostPageUrl, storageKey, widgetId]);

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        if (!message.trim() || !sessionToken) {
            return;
        }

        const userMessage: WidgetMessage = {
            sender: 'user',
            message_text: message.trim(),
            created_at: new Date().toISOString(),
        };
        setMessages((current) => [...current, userMessage]);
        setMessage('');
        setSending(true);

        try {
            const response = await fetch(`${apiBase}/widget/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: sessionToken,
                    message: userMessage.message_text,
                    page_url: hostPageUrl || document.referrer || window.location.href,
                }),
            });

            if (!response.ok) {
                throw new Error('No se pudo enviar el mensaje');
            }

            const data = await response.json();
            setMessages((current) => [
                ...current,
                {
                    sender: 'bot',
                    message_text: data.response,
                    created_at: new Date().toISOString(),
                },
            ]);
        } catch (sendError) {
            setMessages((current) => current.slice(0, -1));
            setError(sendError instanceof Error ? sendError.message : 'Error al enviar el mensaje');
        } finally {
            setSending(false);
        }
    };

    return (
        <main className="min-h-screen bg-[radial-gradient(circle_at_top,#fff7ed,white_48%,#f8fafc)] text-slate-900">
            <div className="flex min-h-screen flex-col rounded-[20px] border border-slate-200 bg-white shadow-2xl">
                <header className="flex items-center justify-between px-4 py-4 text-white" style={{ backgroundColor: primaryColor }}>
                    <div>
                        <p className="text-sm font-semibold">Asistente Web</p>
                        <p className="text-xs text-white/80">Conectado con tu bot principal</p>
                    </div>
                    <button
                        type="button"
                        onClick={() => window.parent.postMessage({ type: 'wa-sales-bot-close' }, '*')}
                        className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold hover:bg-white/25"
                    >
                        Cerrar
                    </button>
                </header>

                <section className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
                    {loading && <p className="text-sm text-slate-500">Cargando conversación...</p>}
                    {error && <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                    {!loading && messages.length === 0 && !error && (
                        <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
                            Escribe tu primer mensaje para iniciar la conversación.
                        </div>
                    )}
                    {messages.map((item, index) => {
                        const isUser = item.sender === 'user';
                        return (
                            <div key={`${item.created_at || 'message'}-${index}`} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                                <div
                                    className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                                        isUser ? 'text-white' : 'border border-slate-200 bg-slate-50 text-slate-900'
                                    }`}
                                    style={isUser ? { backgroundColor: primaryColor } : undefined}
                                >
                                    {item.message_text}
                                </div>
                            </div>
                        );
                    })}
                    {sending && <p className="text-xs text-slate-400">El asistente está escribiendo...</p>}
                </section>

                <footer className="border-t border-slate-200 bg-white px-4 py-4">
                    <form onSubmit={handleSubmit} className="flex items-end gap-2">
                        <textarea
                            value={message}
                            onChange={(event) => setMessage(event.target.value)}
                            rows={2}
                            placeholder="Escribe tu mensaje..."
                            className="min-h-12 flex-1 resize-none rounded-2xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
                        />
                        <button
                            type="submit"
                            disabled={sending || !message.trim() || !sessionId}
                            className="rounded-2xl px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                            style={{ backgroundColor: primaryColor }}
                        >
                            Enviar
                        </button>
                    </form>
                </footer>
            </div>
        </main>
    );
}

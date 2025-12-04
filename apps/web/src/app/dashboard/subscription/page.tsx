'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/components/ui/toast';
import {
    getCurrentSubscription,
    getSubscriptionPlans,
    getSubscriptionUsage,
    getBillingHistory,
    cancelSubscription,
} from '@/lib/api';
import { useUserStore } from '@/stores/user-store';
import { CreditCard, CheckCircle2, TrendingUp, Calendar, AlertCircle, Crown } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface Plan {
    id: number;
    name: string;
    display_name: string;
    price: number;
    features: any;
}

interface Subscription {
    id: number;
    status: string;
    plan: {
        name: string;
        display_name: string;
    };
    current_period_end: string;
    cancel_at_period_end: boolean;
}

interface Usage {
    messages_sent: number;
    messages_limit: number;
    bots_created: number;
    bots_limit: number;
    rag_storage_mb: number;
    rag_storage_limit_mb: number;
}

interface BillingRecord {
    id: number;
    amount: number;
    status: string;
    billing_date: string;
    invoice_url?: string;
}

export default function SubscriptionPage() {
    const { addToast } = useToast();
    const { subscription: storeSubscription, setSubscription } = useUserStore();
    const [loading, setLoading] = useState(true);
    const [plans, setPlans] = useState<Plan[]>([]);
    const [subscription, setSubscriptionLocal] = useState<Subscription | null>(null);
    const [usage, setUsage] = useState<Usage | null>(null);
    const [billingHistory, setBillingHistory] = useState<BillingRecord[]>([]);
    const [canceling, setCanceling] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [plansData, subData, usageData, billingData] = await Promise.all([
                getSubscriptionPlans(),
                getCurrentSubscription(),
                getSubscriptionUsage(),
                getBillingHistory(),
            ]);

            setPlans(plansData);
            setSubscriptionLocal(subData);
            setSubscription(subData);
            setUsage(usageData);
            setBillingHistory(billingData);
        } catch (error: any) {
            addToast('Error al cargar información de suscripción', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleCancelSubscription = async () => {
        if (!confirm('¿Estás seguro de que deseas cancelar tu suscripción? Mantendrás acceso hasta el final del período actual.')) {
            return;
        }

        setCanceling(true);
        try {
            await cancelSubscription(true);
            addToast('Suscripción cancelada. Tendrás acceso hasta el final del período.', 'success');
            loadData();
        } catch (error: any) {
            addToast(error.response?.data?.detail || 'Error al cancelar suscripción', 'error');
        } finally {
            setCanceling(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    const getUsagePercentage = (used: number, limit: number) => {
        return Math.min((used / limit) * 100, 100);
    };

    const getUsageColor = (percentage: number) => {
        if (percentage >= 90) return 'bg-red-600';
        if (percentage >= 70) return 'bg-yellow-600';
        return 'bg-green-600';
    };

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-black dark:text-white">Mi Suscripción</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Administra tu plan, uso y facturación
                </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Current Plan */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Plan Card */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                    <Crown className="w-6 h-6 text-purple-600" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-black dark:text-white">
                                        Plan {subscription?.plan.display_name || 'Starter'}
                                    </h2>
                                    <p className="text-sm text-gray-600">
                                        {subscription?.status === 'active' ? 'Activo' : 'Inactivo'}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-black text-purple-600">
                                    ${plans.find(p => p.name === subscription?.plan.name)?.price || 0}
                                </p>
                                <p className="text-xs text-gray-500">por mes</p>
                            </div>
                        </div>

                        {subscription?.cancel_at_period_end && (
                            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 mb-4 flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-yellow-900">
                                        Suscripción programada para cancelarse
                                    </p>
                                    <p className="text-xs text-yellow-800 mt-1">
                                        Tendrás acceso hasta {subscription?.current_period_end && format(new Date(subscription.current_period_end), "d 'de' MMMM, yyyy", { locale: es })}
                                    </p>
                                </div>
                            </div>
                        )}

                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                            <Calendar className="w-4 h-4" />
                            Renovación:{' '}
                            {subscription?.current_period_end
                                ? format(new Date(subscription.current_period_end), "d 'de' MMMM, yyyy", { locale: es })
                                : 'N/A'}
                        </div>

                        <div className="flex gap-2">
                            <Button variant="outline" className="flex-1">
                                Actualizar plan
                            </Button>
                            {!subscription?.cancel_at_period_end && (
                                <Button
                                    variant="outline"
                                    onClick={handleCancelSubscription}
                                    disabled={canceling}
                                    className="border-red-200 text-red-600 hover:bg-red-50"
                                >
                                    {canceling ? 'Cancelando...' : 'Cancelar plan'}
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Usage Stats */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                        <h3 className="text-lg font-bold text-black dark:text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Uso del período actual
                        </h3>

                        <div className="space-y-4">
                            {/* Messages */}
                            {usage && (
                                <>
                                    <div>
                                        <div className="flex justify-between text-sm mb-2">
                                            <span className="text-gray-700 dark:text-gray-300">Mensajes enviados</span>
                                            <span className="font-bold">
                                                {usage.messages_sent} / {usage.messages_limit}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${getUsageColor(
                                                    getUsagePercentage(usage.messages_sent, usage.messages_limit)
                                                )}`}
                                                style={{
                                                    width: `${getUsagePercentage(usage.messages_sent, usage.messages_limit)}%`,
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Bots */}
                                    <div>
                                        <div className="flex justify-between text-sm mb-2">
                                            <span className="text-gray-700 dark:text-gray-300">Bots creados</span>
                                            <span className="font-bold">
                                                {usage.bots_created} / {usage.bots_limit}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${getUsageColor(
                                                    getUsagePercentage(usage.bots_created, usage.bots_limit)
                                                )}`}
                                                style={{
                                                    width: `${getUsagePercentage(usage.bots_created, usage.bots_limit)}%`,
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Storage */}
                                    <div>
                                        <div className="flex justify-between text-sm mb-2">
                                            <span className="text-gray-700 dark:text-gray-300">Almacenamiento RAG</span>
                                            <span className="font-bold">
                                                {usage.rag_storage_mb.toFixed(1)} MB / {usage.rag_storage_limit_mb} MB
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${getUsageColor(
                                                    getUsagePercentage(usage.rag_storage_mb, usage.rag_storage_limit_mb)
                                                )}`}
                                                style={{
                                                    width: `${getUsagePercentage(
                                                        usage.rag_storage_mb,
                                                        usage.rag_storage_limit_mb
                                                    )}%`,
                                                }}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Billing History */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-6">
                        <h3 className="text-lg font-bold text-black dark:text-white mb-4 flex items-center gap-2">
                            <CreditCard className="w-5 h-5" />
                            Historial de pagos
                        </h3>

                        <div className="space-y-3">
                            {billingHistory.length > 0 ? (
                                billingHistory.slice(0, 5).map((record) => (
                                    <div key={record.id} className="flex items-start justify-between text-sm">
                                        <div>
                                            <p className="font-semibold text-gray-900 dark:text-white">
                                                ${record.amount.toFixed(2)}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {format(new Date(record.billing_date), "d 'de' MMM, yyyy", { locale: es })}
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {record.status === 'paid' ? (
                                                <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold">
                                                    <CheckCircle2 className="w-3 h-3" />
                                                    Pagado
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full text-xs font-semibold">
                                                    Pendiente
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-gray-500 text-center py-4">
                                    No hay historial de pagos
                                </p>
                            )}
                        </div>

                        {billingHistory.length > 5 && (
                            <Button variant="outline" className="w-full mt-4" size="sm">
                                Ver todos los pagos
                            </Button>
                        )}
                    </div>

                    {/* Available Plans Preview */}
                    <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
                        <h3 className="font-bold text-purple-900 mb-2">¿Necesitas más?</h3>
                        <p className="text-sm text-purple-800 mb-3">
                            Actualiza a un plan superior para obtener más mensajes, bots y funciones.
                        </p>
                        <Button className="w-full" size="sm">
                            Ver planes disponibles
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

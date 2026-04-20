"use client"

import { useCallback, useEffect, useState } from "react"
import { Users, DollarSign, TrendingUp, Activity, AlertCircle } from "lucide-react"
import { MetricCard } from "@/components/crm/MetricCard"
import { getCrmMetrics } from "@/lib/api"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

interface CrmMetrics {
    total_active_deals: number
    conversion_rate: number
    total_revenue: number
    total_won_deals: number
}

export default function CrmDashboardPage() {
    const [metrics, setMetrics] = useState<CrmMetrics | null>(null)
    const [loading, setLoading] = useState(true)

    const loadMetrics = useCallback(async () => {
        try {
            const data = await getCrmMetrics()
            setMetrics(data)
        } catch (error) {
            console.error("Error loading metrics:", error)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        void loadMetrics()
    }, [loadMetrics])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <LoadingSpinner size="lg" />
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    title="Total Leads Activos"
                    value={metrics?.total_active_deals || 0}
                    icon={Users}
                    color="blue"
                    trend={{ value: 12, label: "vs mes pasado", positive: true }}
                />
                <MetricCard
                    title="Tasa de Conversión"
                    value={`${metrics?.conversion_rate || 0}%`}
                    icon={TrendingUp}
                    color="purple"
                    trend={{ value: 2.5, label: "vs mes pasado", positive: true }}
                />
                <MetricCard
                    title="Revenue Total"
                    value={`$${metrics?.total_revenue?.toLocaleString() || 0}`}
                    icon={DollarSign}
                    color="green"
                    trend={{ value: 8, label: "vs mes pasado", positive: true }}
                />
                <MetricCard
                    title="Deals Ganados"
                    value={metrics?.total_won_deals || 0}
                    icon={Activity}
                    color="orange"
                />
            </div>

            {/* Recent Activity & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity */}
                <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800 p-6">
                    <h3 className="text-lg font-bold text-black dark:text-white mb-6">Actividad Reciente</h3>
                    <div className="space-y-4">
                        {/* Placeholder activity items */}
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-full text-purple-600 dark:text-purple-400">
                                    <Users size={16} />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-black dark:text-white">
                                        Nuevo lead calificado: <span className="font-bold">Juan Pérez</span>
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">Hace {i * 15} minutos</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Needs Attention */}
                <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800 p-6">
                    <h3 className="text-lg font-bold text-black dark:text-white mb-6 flex items-center gap-2">
                        <AlertCircle className="text-red-500" size={20} />
                        Requiere Atención
                    </h3>
                    <div className="space-y-4">
                        {/* Placeholder alert items */}
                        {[1, 2].map((i) => (
                            <div key={i} className="p-4 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30">
                                <p className="text-sm font-bold text-red-700 dark:text-red-400">
                                    Seguimiento pendiente
                                </p>
                                <p className="text-xs text-red-600 dark:text-red-300 mt-1">
                                    María García no ha respondido en 3 días
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

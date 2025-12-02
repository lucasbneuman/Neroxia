"use client"

import { useState, useEffect } from "react"
import { Search, Filter, MoreHorizontal, Phone, Mail, Calendar } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { getDeals } from "@/lib/api"
import type { Deal } from "@/types"
import { cn } from "@/lib/utils"

const STAGE_COLORS: Record<string, string> = {
    new_lead: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    qualified: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    in_conversation: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    proposal_sent: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
    won: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    lost: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
}

const STAGE_LABELS: Record<string, string> = {
    new_lead: "Nuevo Lead",
    qualified: "Calificado",
    in_conversation: "En Conversación",
    proposal_sent: "Propuesta Enviada",
    won: "Ganado",
    lost: "Perdido",
}

export default function ContactsPage() {
    const [deals, setDeals] = useState<Deal[]>([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState("")
    const [stageFilter, setStageFilter] = useState<string>("all")

    useEffect(() => {
        loadDeals()
    }, [stageFilter])

    const loadDeals = async () => {
        setLoading(true)
        try {
            const stage = stageFilter === "all" ? undefined : stageFilter
            const data = await getDeals(stage)
            setDeals(data)
        } catch (error) {
            console.error("Error loading deals:", error)
        } finally {
            setLoading(false)
        }
    }

    const filteredDeals = deals.filter(deal => {
        if (!searchQuery) return true
        const query = searchQuery.toLowerCase()
        const userName = deal.user?.name?.toLowerCase() || ""
        const userPhone = deal.user?.phone?.toLowerCase() || ""
        const dealTitle = deal.title.toLowerCase()

        return userName.includes(query) || userPhone.includes(query) || dealTitle.includes(query)
    })

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("es-ES", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        })
    }

    return (
        <div className="space-y-6">
            {/* Filters & Search */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white dark:bg-gray-900 p-4 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800">
                <div className="relative w-full sm:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                        placeholder="Buscar por nombre, teléfono..."
                        className="pl-10"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className="flex gap-4 w-full sm:w-auto">
                    <Select value={stageFilter} onValueChange={setStageFilter}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Filtrar por etapa" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todas las etapas</SelectItem>
                            {Object.entries(STAGE_LABELS).map(([key, label]) => (
                                <SelectItem key={key} value={key}>{label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Button variant="outline" className="gap-2">
                        <Filter size={16} />
                        Más Filtros
                    </Button>
                </div>
            </div>

            {/* Contacts Table */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-800">
                                <th className="text-left py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Contacto</th>
                                <th className="text-left py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Etapa</th>
                                <th className="text-left py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Valor</th>
                                <th className="text-left py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Probabilidad</th>
                                <th className="text-left py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Última Actividad</th>
                                <th className="text-right py-4 px-6 text-xs font-bold text-gray-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="py-12 text-center">
                                        <LoadingSpinner size="lg" />
                                    </td>
                                </tr>
                            ) : filteredDeals.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="py-12 text-center text-gray-500 dark:text-gray-400">
                                        No se encontraron contactos
                                    </td>
                                </tr>
                            ) : (
                                filteredDeals.map((deal) => (
                                    <tr key={deal.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold">
                                                    {deal.user?.name?.charAt(0) || deal.user?.phone?.charAt(1) || "?"}
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <p className="font-bold text-black dark:text-white">
                                                            {deal.user?.name || "Sin nombre"}
                                                        </p>
                                                        {deal.source === "test" && (
                                                            <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-bold rounded-full">
                                                                TEST
                                                            </span>
                                                        )}
                                                    </div>
                                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                                        <Phone size={12} />
                                                        {deal.user?.phone}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6">
                                            <span className={cn(
                                                "px-3 py-1 rounded-full text-xs font-bold",
                                                STAGE_COLORS[deal.stage] || "bg-gray-100 text-gray-700"
                                            )}>
                                                {STAGE_LABELS[deal.stage] || deal.stage}
                                            </span>
                                        </td>
                                        <td className="py-4 px-6">
                                            <p className="font-bold text-black dark:text-white">
                                                ${deal.value.toLocaleString()}
                                            </p>
                                            <p className="text-xs text-gray-500">{deal.currency}</p>
                                        </td>
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2">
                                                <div className="w-16 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-purple-600 rounded-full"
                                                        style={{ width: `${deal.probability}%` }}
                                                    />
                                                </div>
                                                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                                    {deal.probability}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                                <Calendar size={14} />
                                                {formatDate(deal.updated_at)}
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 text-right">
                                            <Button variant="ghost" size="icon" className="hover:bg-gray-100 dark:hover:bg-gray-800">
                                                <MoreHorizontal size={18} className="text-gray-500" />
                                            </Button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination (Placeholder) */}
                <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
                    <p className="text-sm text-gray-500">
                        Mostrando {filteredDeals.length} resultados
                    </p>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" disabled>Anterior</Button>
                        <Button variant="outline" size="sm" disabled>Siguiente</Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

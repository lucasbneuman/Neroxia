"use client"

import { useState, useEffect } from "react"
import { RefreshCw } from "lucide-react"
import {
    DndContext,
    DragOverlay,
    useSensor,
    useSensors,
    PointerSensor,
    type DragEndEvent,
    type DragStartEvent
} from "@dnd-kit/core"
import { Button } from "@/components/ui/button"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { PipelineColumn } from "@/components/crm/PipelineColumn"
import { DealDetailModal } from "@/components/crm/DealDetailModal"
import { getDeals, updateDealStage } from "@/lib/api"
import type { Deal } from "@/types"

const PIPELINE_STAGES = [
    { key: "new_lead", label: "Nuevo Lead", color: "gray" },
    { key: "qualified", label: "Calificado", color: "blue" },
    { key: "in_conversation", label: "En Conversación", color: "yellow" },
    { key: "proposal_sent", label: "Propuesta Enviada", color: "orange" },
    { key: "won", label: "Ganado", color: "green" },
    { key: "lost", label: "Perdido", color: "red" },
]

export default function PipelinePage() {
    const [deals, setDeals] = useState<Deal[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [activeId, setActiveId] = useState<string | null>(null)

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    )

    useEffect(() => {
        loadDeals()
    }, [])

    const loadDeals = async () => {
        setLoading(true)
        try {
            const data = await getDeals()
            setDeals(data)
        } catch (error) {
            console.error("Error loading deals:", error)
        } finally {
            setLoading(false)
        }
    }

    const getDealsByStage = (stage: string) => {
        return deals.filter(deal => deal.stage === stage)
    }

    const handleDealClick = (deal: Deal) => {
        if (activeId) return // Don't open modal if dragging
        setSelectedDeal(deal)
        setIsModalOpen(true)
    }

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string)
    }

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event
        setActiveId(null)

        if (!over) return

        const dealId = parseInt(active.id as string)
        const newStage = over.id as string
        const deal = deals.find(d => d.id === dealId)

        if (!deal || deal.stage === newStage) return

        // Optimistic update
        const oldStage = deal.stage
        setDeals(deals.map(d =>
            d.id === dealId
                ? { ...d, stage: newStage as Deal['stage'], manually_qualified: true }
                : d
        ))

        try {
            await updateDealStage(dealId, newStage)
        } catch (error) {
            console.error("Error updating deal stage:", error)
            // Rollback on error
            setDeals(deals.map(d =>
                d.id === dealId
                    ? { ...d, stage: oldStage }
                    : d
            ))
            alert("Error al actualizar la etapa del deal")
        }
    }

    const totalValue = deals.reduce((sum, deal) => sum + deal.value, 0)
    const activeDeals = deals.filter(deal => deal.stage !== "won" && deal.stage !== "lost").length

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <LoadingSpinner size="lg" />
            </div>
        )
    }

    return (
        <DndContext
            sensors={sensors}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
        >
            <div className="space-y-6">
                {/* Header Stats */}
                <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800 p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex gap-8">
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 font-bold uppercase">
                                    Deals Activos
                                </p>
                                <p className="text-3xl font-black text-black dark:text-white mt-1">
                                    {activeDeals}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 font-bold uppercase">
                                    Valor Total
                                </p>
                                <p className="text-3xl font-black text-black dark:text-white mt-1">
                                    ${totalValue.toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 font-bold uppercase">
                                    Ganados
                                </p>
                                <p className="text-3xl font-black text-green-600 dark:text-green-400 mt-1">
                                    {getDealsByStage("won").length}
                                </p>
                            </div>
                        </div>
                        <Button
                            variant="outline"
                            onClick={loadDeals}
                            className="gap-2"
                        >
                            <RefreshCw size={16} />
                            Actualizar
                        </Button>
                    </div>
                </div>

                {/* Pipeline Board */}
                <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800 p-6">
                    <div className="overflow-x-auto">
                        <div className="flex gap-4 pb-4 min-w-max">
                            {PIPELINE_STAGES.map((stage) => (
                                <PipelineColumn
                                    key={stage.key}
                                    title={stage.label}
                                    stage={stage.key}
                                    deals={getDealsByStage(stage.key)}
                                    color={stage.color}
                                    onDealClick={handleDealClick}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Info Message */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
                    <p className="text-sm text-blue-700 dark:text-blue-400">
                        💡 <strong>Tip:</strong> Arrastra los deals entre columnas para cambiar su etapa. Esto activará el modo manual para evitar que el bot lo cambie automáticamente.
                    </p>
                </div>
            </div>

            {/* Deal Detail Modal */}
            <DealDetailModal
                deal={selectedDeal}
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false)
                    setSelectedDeal(null)
                    loadDeals() // Refresh to get latest data
                }}
            />
        </DndContext>
    )
}

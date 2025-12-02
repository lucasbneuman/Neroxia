import { useDraggable, useDroppable } from "@dnd-kit/core"
import { cn } from "@/lib/utils"
import type { Deal } from "@/types"

interface PipelineColumnProps {
    title: string
    stage: string
    deals: Deal[]
    color: string
    onDealClick?: (deal: Deal) => void
}

const STAGE_COLORS: Record<string, string> = {
    new_lead: "border-gray-300 dark:border-gray-700",
    qualified: "border-blue-300 dark:border-blue-700",
    in_conversation: "border-yellow-300 dark:border-yellow-700",
    proposal_sent: "border-orange-300 dark:border-orange-700",
    won: "border-green-300 dark:border-green-700",
    lost: "border-red-300 dark:border-red-700",
}

function DraggableDealCard({ deal, stage, onDealClick }: { deal: Deal; stage: string; onDealClick?: (deal: Deal) => void }) {
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id: deal.id.toString(),
        data: { deal },
    })

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...listeners}
            {...attributes}
            onClick={() => onDealClick?.(deal)}
            className={cn(
                "bg-white dark:bg-gray-800 p-4 rounded-xl shadow-soft border-2 cursor-grab active:cursor-grabbing transition-all hover:shadow-medium hover:scale-[1.02]",
                STAGE_COLORS[stage] || "border-gray-300 dark:border-gray-700",
                isDragging && "opacity-50 rotate-3 scale-105 z-50 shadow-2xl"
            )}
        >
            <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-black dark:text-white text-sm">
                    {deal.title}
                </h4>
                {deal.source === "test" && (
                    <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-bold rounded-full">
                        TEST
                    </span>
                )}
            </div>

            <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold text-xs">
                    {deal.user?.name?.charAt(0) || deal.user?.phone?.charAt(1) || "?"}
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
                        {deal.user?.name || "Sin nombre"}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {deal.user?.phone}
                    </p>
                </div>
            </div>

            <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-green-600 dark:text-green-400">
                    ${deal.value.toLocaleString()}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                    {deal.probability}%
                </span>
            </div>
        </div>
    )
}

export function PipelineColumn({ title, stage, deals, color, onDealClick }: PipelineColumnProps) {
    const { setNodeRef, isOver } = useDroppable({
        id: stage,
    })

    const totalValue = deals.reduce((sum, deal) => sum + deal.value, 0)

    return (
        <div
            ref={setNodeRef}
            className={cn(
                "flex flex-col min-w-[280px] bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-4 border-2 transition-colors",
                isOver ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20" : "border-gray-200 dark:border-gray-800"
            )}
        >
            {/* Header */}
            <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold text-black dark:text-white text-sm uppercase tracking-wide">
                        {title}
                    </h3>
                    <span className="px-2 py-1 bg-white dark:bg-gray-800 rounded-full text-xs font-bold text-gray-600 dark:text-gray-400">
                        {deals.length}
                    </span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                    ${totalValue.toLocaleString()} total
                </p>
            </div>

            {/* Deals */}
            <div className="flex-1 space-y-3 overflow-y-auto min-h-[200px]">
                {deals.length === 0 ? (
                    <div className="flex items-center justify-center h-32 text-gray-400 dark:text-gray-600 text-sm border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl">
                        Arrastra deals aquí
                    </div>
                ) : (
                    deals.map((deal) => (
                        <DraggableDealCard
                            key={deal.id}
                            deal={deal}
                            stage={stage}
                            onDealClick={onDealClick}
                        />
                    ))
                )}
            </div>
        </div>
    )
}

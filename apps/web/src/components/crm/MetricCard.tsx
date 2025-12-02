import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
    title: string
    value: string | number
    icon: LucideIcon
    trend?: {
        value: number
        label: string
        positive: boolean
    }
    color?: "purple" | "blue" | "green" | "orange"
}

export function MetricCard({ title, value, icon: Icon, trend, color = "purple" }: MetricCardProps) {
    const colorStyles = {
        purple: "bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400",
        blue: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
        green: "bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400",
        orange: "bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400",
    }

    return (
        <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-soft border border-gray-100 dark:border-gray-800">
            <div className="flex items-center justify-between mb-4">
                <div className={cn("p-3 rounded-xl", colorStyles[color])}>
                    <Icon size={24} />
                </div>
                {trend && (
                    <div className={cn(
                        "text-xs font-bold px-2 py-1 rounded-full",
                        trend.positive
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    )}>
                        {trend.positive ? "+" : ""}{trend.value}% {trend.label}
                    </div>
                )}
            </div>
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider">{title}</h3>
            <p className="text-3xl font-black text-black dark:text-white mt-1">{value}</p>
        </div>
    )
}

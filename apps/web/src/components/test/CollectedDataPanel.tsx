"use client"

import type { CollectedData } from "@/types"

interface CollectedDataPanelProps {
    data: CollectedData
}

export function CollectedDataPanel({ data }: CollectedDataPanelProps) {
    const dataFields = [
        { icon: "🆔", label: "ID", value: data.user_id, color: "purple" },
        { icon: "📝", label: "Nombre", value: data.name, color: "blue" },
        { icon: "📧", label: "Email", value: data.email, color: "green" },
        { icon: "📱", label: "Teléfono", value: data.phone, color: "orange" },
        { icon: "🕐", label: "Último contacto", value: data.last_contact, color: "gray" },
        { icon: "🎯", label: "Intención", value: data.intent, color: "red" },
        { icon: "😊", label: "Sentimiento", value: data.sentiment, color: "yellow" },
        { icon: "📊", label: "Etapa", value: data.stage, color: "indigo" },
        { icon: "💡", label: "Necesidades", value: data.needs, color: "pink" },
        { icon: "👨‍💼", label: "Solicita Humano", value: data.requests_human, color: "teal" },
    ]

    const getColorClasses = (color: string) => {
        const colors: Record<string, string> = {
            purple: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800",
            blue: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
            green: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
            orange: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800",
            gray: "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700",
            red: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
            yellow: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800",
            indigo: "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800",
            pink: "bg-pink-50 dark:bg-pink-900/20 border-pink-200 dark:border-pink-800",
            teal: "bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800",
        }
        return colors[color] || colors.gray
    }

    return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-soft overflow-hidden h-full flex flex-col">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-500 p-4">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Datos Recolectados
                </h2>
                <p className="text-purple-100 text-xs mt-1">Información extraída en tiempo real</p>
            </div>

            {/* Content */}
            <div className="flex-1 p-4 space-y-2 overflow-y-auto">
                {dataFields.map((field, index) => (
                    <div
                        key={index}
                        className={`p-3 border rounded-xl transition-all hover:shadow-md ${getColorClasses(field.color)}`}
                    >
                        <div className="flex items-start gap-2">
                            <span className="text-xl flex-shrink-0">{field.icon}</span>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                                    {field.label}
                                </p>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-0.5 break-words">
                                    {field.value}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}

                {/* Notes Section */}
                {data.notes && data.notes !== "-" && (
                    <div className="mt-4 p-4 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-800 rounded-xl">
                        <div className="flex items-start gap-2">
                            <span className="text-xl flex-shrink-0">📋</span>
                            <div className="flex-1">
                                <p className="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wide mb-1">
                                    Notas
                                </p>
                                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                                    {data.notes}
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

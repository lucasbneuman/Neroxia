"use client"

import type { User } from "@/types"

interface UserDataPanelProps {
    user: User | null
}

export function UserDataPanel({ user }: UserDataPanelProps) {
    if (!user) {
        return (
            <div className="p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-center shadow-soft">
                <div className="text-gray-400 dark:text-gray-500">
                    <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <p className="text-sm font-bold">Selecciona una conversación</p>
                </div>
            </div>
        )
    }

    const getModeDisplay = () => {
        switch (user.conversation_mode) {
            case "AUTO":
                return { text: "Automático", color: "text-green-600 dark:text-green-400", bg: "bg-green-50 dark:bg-green-900/20" }
            case "MANUAL":
                return { text: "Manual", color: "text-red-600 dark:text-red-400", bg: "bg-red-50 dark:bg-red-900/20" }
            case "NEEDS_ATTENTION":
                return { text: "Necesita Atención", color: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-50 dark:bg-yellow-900/20" }
            default:
                return { text: "Automático", color: "text-green-600 dark:text-green-400", bg: "bg-green-50 dark:bg-green-900/20" }
        }
    }

    const formatDate = (dateString?: string) => {
        if (!dateString) return "N/A"
        const date = new Date(dateString)
        return date.toLocaleString("es-ES", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        })
    }

    const mode = getModeDisplay()

    return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-soft overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-500 p-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {user.name || "Sin nombre"}
                </h3>
                <p className="text-purple-100 text-xs mt-1">{user.phone}</p>
            </div>

            {/* Content */}
            <div className="p-4 space-y-3">
                {/* Mode Badge */}
                <div className={`${mode.bg} ${mode.color} px-3 py-2 rounded-xl text-sm font-bold text-center`}>
                    {mode.text}
                </div>

                {/* Info Grid */}
                <div className="space-y-2 text-sm">
                    {user.email && (
                        <div className="flex items-start gap-2">
                            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <div className="flex-1">
                                <p className="text-gray-500 dark:text-gray-400 text-xs">Email</p>
                                <p className="text-gray-900 dark:text-gray-100 font-medium">{user.email}</p>
                            </div>
                        </div>
                    )}

                    <div className="flex items-start gap-2">
                        <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                        <div className="flex-1">
                            <p className="text-gray-500 dark:text-gray-400 text-xs">Total Mensajes</p>
                            <p className="text-gray-900 dark:text-gray-100 font-medium">{user.total_messages}</p>
                        </div>
                    </div>

                    <div className="flex items-start gap-2">
                        <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                            <p className="text-gray-500 dark:text-gray-400 text-xs">Última actividad</p>
                            <p className="text-gray-900 dark:text-gray-100 font-medium text-xs">{formatDate(user.last_message_at)}</p>
                        </div>
                    </div>

                    {user.sentiment && (
                        <div className="flex items-start gap-2">
                            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div className="flex-1">
                                <p className="text-gray-500 dark:text-gray-400 text-xs">Sentimiento</p>
                                <p className="text-gray-900 dark:text-gray-100 font-medium capitalize">{user.sentiment}</p>
                            </div>
                        </div>
                    )}

                    {user.stage && (
                        <div className="flex items-start gap-2">
                            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <div className="flex-1">
                                <p className="text-gray-500 dark:text-gray-400 text-xs">Etapa</p>
                                <p className="text-gray-900 dark:text-gray-100 font-medium capitalize">{user.stage}</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Summary */}
                {user.conversation_summary && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-start gap-2">
                            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <div className="flex-1">
                                <p className="text-gray-500 dark:text-gray-400 text-xs font-bold mb-1">Resumen de conversación</p>
                                <p className="text-gray-700 dark:text-gray-300 text-xs leading-relaxed">{user.conversation_summary}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

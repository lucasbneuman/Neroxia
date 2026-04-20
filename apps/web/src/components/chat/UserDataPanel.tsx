"use client"

import { useState } from "react"
import type { User } from "@/types"
import { Trash2 } from "lucide-react"
import { deleteConversationByUserId } from "@/lib/api"

interface UserDataPanelProps {
    user: User | null
    onConversationDeleted?: () => void
}

export function UserDataPanel({ user, onConversationDeleted }: UserDataPanelProps) {
    const [showDeleteDialog, setShowDeleteDialog] = useState(false)
    const [deleteFromCRM, setDeleteFromCRM] = useState(false)
    const [isDeleting, setIsDeleting] = useState(false)

    const handleDelete = async () => {
        if (!user) return

        setIsDeleting(true)
        try {
            const result = await deleteConversationByUserId(user.id, deleteFromCRM)
            console.log("Conversation deleted:", result)

            setShowDeleteDialog(false)
            setDeleteFromCRM(false)

            // Notify parent to refresh
            onConversationDeleted?.()
        } catch (error) {
            console.error("Error deleting conversation:", error)
            alert("Error al eliminar la conversación")
        } finally {
            setIsDeleting(false)
        }
    }

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
        <>
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-soft overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-purple-500 p-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {user.name || "Sin nombre"}
                    </h3>
                    <p className="text-purple-100 text-xs mt-1">{user.display_identifier || user.phone || user.channel_user_id || `Usuario ${user.id}`}</p>
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

                        {user.whatsapp_profile_name && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Perfil WhatsApp</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium">{user.whatsapp_profile_name}</p>
                                </div>
                            </div>
                        )}

                        {user.country_code && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">País</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium">{user.country_code}</p>
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

                        {user.media_count !== undefined && user.media_count > 0 && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Archivos Multimedia</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium">{user.media_count}</p>
                                </div>
                            </div>
                        )}

                        {user.location_shared && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Ubicación</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium">Compartida ✓</p>
                                </div>
                            </div>
                        )}

                        <div className="flex items-start gap-2">
                            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div className="flex-1">
                                <p className="text-gray-500 dark:text-gray-400 text-xs">Última actividad</p>
                                <p className="text-gray-900 dark:text-gray-100 font-medium text-xs">{formatDate(user.last_message_at)}</p>
                            </div>
                        </div>

                        {user.first_contact_timestamp && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Primer contacto</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium text-xs">{formatDate(user.first_contact_timestamp)}</p>
                                </div>
                            </div>
                        )}

                        {user.created_at && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Registrado</p>
                                    <p className="text-gray-900 dark:text-gray-100 font-medium text-xs">{formatDate(user.created_at)}</p>
                                </div>
                            </div>
                        )}

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

                        {user.intent_score !== undefined && (
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                <div className="flex-1">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs">Intención de Compra</p>
                                    <div className="flex items-center gap-2 mt-1">
                                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                            <div
                                                className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all"
                                                style={{ width: `${user.intent_score * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-gray-900 dark:text-gray-100 font-bold text-xs">
                                            {Math.round(user.intent_score * 100)}%
                                        </span>
                                    </div>
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

                    {/* Delete Button */}
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button
                            onClick={() => setShowDeleteDialog(true)}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl font-bold text-sm hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                        >
                            <Trash2 size={16} />
                            Eliminar Conversación
                        </button>
                    </div>
                </div>
            </div>

            {/* Delete Confirmation Dialog */}
            {showDeleteDialog && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                                <Trash2 className="text-red-600 dark:text-red-400" size={24} />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-black dark:text-white">Eliminar Conversación</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Esta acción no se puede deshacer</p>
                            </div>
                        </div>

                        <div className="mb-6">
                            <p className="text-gray-700 dark:text-gray-300 mb-4">
                                ¿Estás seguro de que deseas eliminar la conversación con <span className="font-bold">{user.name || user.display_identifier || user.phone || user.channel_user_id}</span>?
                            </p>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                Se eliminarán todos los mensajes y datos del usuario.
                            </p>

                            {/* CRM Checkbox */}
                            <label className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-900/70 transition-colors">
                                <input
                                    type="checkbox"
                                    checked={deleteFromCRM}
                                    onChange={(e) => setDeleteFromCRM(e.target.checked)}
                                    className="mt-0.5 w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                                />
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-gray-900 dark:text-gray-100">
                                        También eliminar del CRM
                                    </p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                        Eliminar todos los deals, notas y tags asociados a este contacto
                                    </p>
                                </div>
                            </label>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => {
                                    setShowDeleteDialog(false)
                                    setDeleteFromCRM(false)
                                }}
                                disabled={isDeleting}
                                className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-bold hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleDelete}
                                disabled={isDeleting}
                                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {isDeleting ? (
                                    <>
                                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                        </svg>
                                        Eliminando...
                                    </>
                                ) : (
                                    <>
                                        <Trash2 size={16} />
                                        Eliminar
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}

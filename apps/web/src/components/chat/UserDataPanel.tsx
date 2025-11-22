"use client"

import type { User } from "@/types"

interface UserDataPanelProps {
    user: User | null
}

export function UserDataPanel({ user }: UserDataPanelProps) {
    if (!user) {
        return (
            <div className="p-4 bg-gray-50 border border-gray-300 rounded text-center text-gray-400">
                Selecciona una conversación
            </div>
        )
    }

    const getModeDisplay = () => {
        switch (user.conversation_mode) {
            case "AUTO":
                return "🟢 Automático"
            case "MANUAL":
                return "🔴 Manual"
            case "NEEDS_ATTENTION":
                return "⚠️ Necesita Atención"
            default:
                return "🟢 Automático"
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

    return (
        <div className="p-4 bg-gray-50 border border-gray-300 rounded">
            <h3 className="text-lg font-semibold mb-3 text-black">
                {user.name || "Sin nombre"}
            </h3>

            <div className="space-y-2 text-sm">
                <div>
                    <strong className="text-black">Teléfono:</strong>{" "}
                    <span className="text-gray-700">{user.phone}</span>
                </div>

                <div>
                    <strong className="text-black">Email:</strong>{" "}
                    <span className="text-gray-700">{user.email || "No registrado"}</span>
                </div>

                <div>
                    <strong className="text-black">Modo:</strong>{" "}
                    <span className="text-gray-700">{getModeDisplay()}</span>
                </div>

                <div>
                    <strong className="text-black">Total Mensajes:</strong>{" "}
                    <span className="text-gray-700">{user.total_messages}</span>
                </div>

                <div>
                    <strong className="text-black">Última actividad:</strong>{" "}
                    <span className="text-gray-700">{formatDate(user.last_message_at)}</span>
                </div>

                {user.sentiment && (
                    <div>
                        <strong className="text-black">Sentimiento:</strong>{" "}
                        <span className="text-gray-700">{user.sentiment}</span>
                    </div>
                )}

                {user.stage && (
                    <div>
                        <strong className="text-black">Etapa:</strong>{" "}
                        <span className="text-gray-700">{user.stage}</span>
                    </div>
                )}

                {user.conversation_summary && (
                    <div className="mt-3 pt-3 border-t border-gray-300">
                        <strong className="text-black block mb-1">Resumen:</strong>
                        <p className="text-gray-700 text-xs">{user.conversation_summary}</p>
                    </div>
                )}
            </div>
        </div>
    )
}

"use client"

import { useEffect, useState } from "react"
import type { Conversation } from "@/types"
import { getConversations } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { ChannelBadge } from "@/components/ui/channel-badge"
import { cn } from "@/lib/utils"

interface ConversationListProps {
    onSelectConversation: (userId: number) => void
    selectedUserId: number | null
    autoRefresh?: boolean
    channelFilter?: "whatsapp" | "instagram" | "messenger" | "web"
}

export function ConversationList({
    onSelectConversation,
    selectedUserId,
    autoRefresh = true,
    channelFilter
}: ConversationListProps) {
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchConversations = async () => {
        try {
            setError(null)
            const data = await getConversations()
            setConversations(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error al cargar conversaciones")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchConversations()

        if (autoRefresh) {
            const interval = setInterval(fetchConversations, 5000) // Refresh every 5 seconds
            return () => clearInterval(interval)
        }
    }, [autoRefresh, channelFilter])

    const getModeIndicator = (mode: string) => {
        switch (mode) {
            case "AUTO":
                return "🟢"
            case "MANUAL":
                return "🔴"
            case "NEEDS_ATTENTION":
                return "⚠️"
            default:
                return "🟢"
        }
    }

    const formatTimestamp = (dateString?: string) => {
        if (!dateString) return ""
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)

        if (diffMins < 1) return "Ahora"
        if (diffMins < 60) return `${diffMins}m`
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h`
        return date.toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit" })
    }

    if (loading) {
        return (
            <div className="p-4 text-center text-gray-400">
                Cargando conversaciones...
            </div>
        )
    }

    if (error) {
        return (
            <div className="p-4">
                <div className="text-red-600 text-sm mb-2">❌ {error}</div>
                <Button onClick={fetchConversations} size="sm" variant="secondary">
                    Reintentar
                </Button>
            </div>
        )
    }

    // Apply channel filter
    const filteredConversations = channelFilter
        ? conversations.filter(conv => conv.user?.channel === channelFilter)
        : conversations

    if (filteredConversations.length === 0) {
        return (
            <div className="p-4 text-center text-gray-400">
                {channelFilter
                    ? `No hay conversaciones en ${channelFilter}`
                    : "No hay conversaciones activas"}
            </div>
        )
    }

    return (
        <div className="space-y-1">
            <div className="flex justify-between items-center px-3 py-2 border-b border-gray-300">
                <h3 className="font-semibold text-sm text-black dark:text-white">Chats Activos</h3>
                <Button onClick={fetchConversations} size="sm" variant="secondary">
                    🔄
                </Button>
            </div>

            {filteredConversations.map((conversation) => {
                // Skip conversations without user data (Bug #2 fix)
                if (!conversation.user) {
                    console.warn('Conversation missing user data:', conversation)
                    return null
                }

                // Safe access with optional chaining and fallbacks
                const displayName = conversation.user?.name || conversation.user?.display_identifier || conversation.user?.phone || 'Unknown'
                const isSelected = conversation.user?.id === selectedUserId
                const lastMessagePreview = conversation.last_message?.length > 50
                    ? conversation.last_message.substring(0, 50) + "..."
                    : conversation.last_message || ''

                return (
                    <div
                        key={conversation.user.id}
                        onClick={() => onSelectConversation(conversation.user.id)}
                        className={cn(
                            "p-3 border-b border-gray-200 cursor-pointer transition-colors hover:bg-gray-100",
                            isSelected && "bg-gray-100",
                            conversation.unread && "font-semibold"
                        )}
                    >
                        <div className="flex justify-between items-start mb-1">
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                <span className="text-sm text-black dark:text-white">
                                    {getModeIndicator(conversation.user?.conversation_mode || 'AUTO')}
                                </span>
                                <span className="text-sm text-black dark:text-white truncate">
                                    {displayName}
                                </span>
                                <ChannelBadge
                                    channel={conversation.user?.channel || 'whatsapp'}
                                    variant="outline"
                                />
                            </div>
                            <span className="text-xs text-gray-500 ml-2 shrink-0">
                                {formatTimestamp(conversation.user?.last_message_at)}
                            </span>
                        </div>
                        <div className="text-xs text-gray-600">
                            {lastMessagePreview}
                        </div>
                        {conversation.user.origin_host && (
                            <div className="text-[11px] text-gray-500 mt-1 truncate">
                                {conversation.user.origin_host}
                            </div>
                        )}
                    </div>
                )
            })}
        </div>
    )
}

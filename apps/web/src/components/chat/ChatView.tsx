"use client"

import { useEffect, useState, useRef } from "react"
import type { Message } from "@/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { sendManualMessage } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Send, Paperclip, Mic, Smile } from "lucide-react"

interface ChatViewProps {
    phone: string
    messages: Message[]
    conversationMode: string
    onMessageSent?: () => void
}

export function ChatView({ phone, messages, conversationMode, onMessageSent }: ChatViewProps) {
    const [messageText, setMessageText] = useState("")
    const [sending, setSending] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const handleSendMessage = async () => {
        if (!messageText.trim()) return

        if (conversationMode !== "MANUAL") {
            setError("Solo puedes enviar mensajes en modo MANUAL")
            return
        }

        try {
            setSending(true)
            setError(null)

            await sendManualMessage(phone, messageText)

            setMessageText("")
            onMessageSent?.()
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error al enviar mensaje")
        } finally {
            setSending(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp)
        return date.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })
    }

    const isManualMode = conversationMode === "MANUAL"

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.length === 0 ? (
                    <div className="text-center text-gray-400 mt-8">
                        No hay mensajes en esta conversación
                    </div>
                ) : (
                    messages.map((message) => {
                        const isBot = message.sender === "bot"
                        const isManual = message.message_metadata?.manual

                        return (
                            <div
                                key={message.id}
                                className={cn(
                                    "flex",
                                    isBot ? "justify-start" : "justify-end"
                                )}
                            >
                                <div
                                    className={cn(
                                        "max-w-[70%] rounded-lg px-4 py-2",
                                        isBot
                                            ? "bg-gray-100 dark:bg-gray-700 text-black dark:text-white"
                                            : "bg-blue-500 text-white"
                                    )}
                                >
                                    <div className="text-sm whitespace-pre-wrap break-words">
                                        {message.message_text}
                                    </div>
                                    <div
                                        className={cn(
                                            "text-xs mt-1 flex items-center gap-1",
                                            isBot ? "text-gray-500" : "text-blue-100"
                                        )}
                                    >
                                        <span>{formatTime(message.timestamp)}</span>
                                        {isManual && (
                                            <span className="text-xs">
                                                • Manual ({message.message_metadata?.agent?.split("@")[0]})
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )
                    })
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800">
                {error && (
                    <div className="text-red-600 text-sm mb-2">
                        ❌ {error}
                    </div>
                )}

                <div className="flex items-end gap-2">
                    {/* Emoji Button (placeholder) */}
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        disabled={!isManualMode}
                        className="flex-shrink-0 px-2"
                        title="Emojis (próximamente)"
                    >
                        <Smile className="h-5 w-5 text-gray-400" />
                    </Button>

                    {/* Attachment Button (placeholder) */}
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        disabled={!isManualMode}
                        className="flex-shrink-0 px-2"
                        title="Adjuntar archivo (próximamente)"
                    >
                        <Paperclip className="h-5 w-5 text-gray-400" />
                    </Button>

                    {/* Text Input */}
                    <Input
                        value={messageText}
                        onChange={(e) => setMessageText(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={
                            isManualMode
                                ? "Escribe un mensaje..."
                                : "Activa modo MANUAL para enviar mensajes"
                        }
                        disabled={!isManualMode || sending}
                        className="flex-1"
                    />

                    {/* Voice Button (placeholder) */}
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        disabled={!isManualMode}
                        className="flex-shrink-0 px-2"
                        title="Mensaje de voz (próximamente)"
                    >
                        <Mic className="h-5 w-5 text-gray-400" />
                    </Button>

                    {/* Send Button */}
                    <Button
                        onClick={handleSendMessage}
                        disabled={!isManualMode || !messageText.trim() || sending}
                        className="flex-shrink-0"
                    >
                        {sending ? (
                            "Enviando..."
                        ) : (
                            <>
                                <Send className="h-4 w-4 mr-1" />
                                Enviar
                            </>
                        )}
                    </Button>
                </div>

                {!isManualMode && (
                    <div className="text-xs text-gray-500 mt-2 text-center">
                        💡 Haz clic en "Tomar Control" para activar el modo manual y enviar mensajes
                    </div>
                )}
            </div>
        </div>
    )
}

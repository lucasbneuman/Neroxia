"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { Message } from "@/types"

interface TestChatProps {
    messages: Message[]
    onSendMessage: (message: string) => void
    onClear: () => void
    loading?: boolean
}

export function TestChat({ messages, onSendMessage, onClear, loading }: TestChatProps) {
    const [message, setMessage] = useState("")

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!message.trim() || loading) return

        onSendMessage(message)
        setMessage("")
    }

    return (
        <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-black">💬 Conversación de Prueba</h2>
                <Button onClick={onClear} variant="secondary" size="sm">
                    Limpiar Chat
                </Button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 border border-gray-300 rounded p-4 bg-gray-50 overflow-y-auto mb-4" style={{ height: "500px" }}>
                {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-400">
                        Envía un mensaje para comenzar la prueba
                    </div>
                ) : (
                    <div className="space-y-3">
                        {messages.map((msg, index) => {
                            const isUser = msg.sender === "user"
                            return (
                                <div
                                    key={index}
                                    className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                                >
                                    <div
                                        className={`max-w-[70%] rounded px-4 py-2 text-sm ${isUser
                                                ? "bg-black text-white"
                                                : "bg-white text-black border border-gray-300"
                                            }`}
                                    >
                                        <p className="whitespace-pre-wrap break-words">{msg.message_text}</p>
                                    </div>
                                </div>
                            )
                        })}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-white border border-gray-300 rounded px-4 py-2">
                                    <div className="flex space-x-2">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Message Input */}
            <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Escribe tu mensaje..."
                    disabled={loading}
                    className="flex-1"
                />
                <Button type="submit" disabled={loading || !message.trim()} variant="primary">
                    Enviar
                </Button>
            </form>
        </div>
    )
}

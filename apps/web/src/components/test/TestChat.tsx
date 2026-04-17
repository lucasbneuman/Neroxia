"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
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
        <div className="flex flex-col h-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-soft overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-500 p-4 flex justify-between items-center">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    Conversación de Prueba
                </h2>
                <Button onClick={onClear} variant="secondary" size="sm" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
                    Limpiar Chat
                </Button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 overflow-y-auto" style={{ height: "500px" }}>
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500">
                        <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p className="font-bold">Envía un mensaje para comenzar la prueba</p>
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
                                        className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm shadow-soft ${isUser
                                                ? "bg-gradient-to-r from-purple-600 to-purple-500 text-white"
                                                : "bg-white dark:bg-gray-700 text-black dark:text-white border border-gray-200 dark:border-gray-600"
                                            }`}
                                    >
                                        <p className="whitespace-pre-wrap break-words">{msg.message_text}</p>
                                    </div>
                                </div>
                            )
                        })}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-2xl px-4 py-3 shadow-soft">
                                    <div className="flex space-x-2">
                                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <Input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Escribe tu mensaje..."
                        disabled={loading}
                        className="flex-1"
                    />
                    <Button type="submit" disabled={loading || !message.trim()} variant="primary">
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <LoadingSpinner size="sm" />
                                Enviando...
                            </span>
                        ) : (
                            "Enviar"
                        )}
                    </Button>
                </form>
            </div>
        </div>
    )
}

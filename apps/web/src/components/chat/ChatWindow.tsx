"use client"

import { useEffect, useRef } from "react"
import type { Message } from "@/types"
import { MessageBubble } from "./MessageBubble"

interface ChatWindowProps {
    messages: Message[]
    loading?: boolean
}

export function ChatWindow({ messages, loading }: ChatWindowProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    return (
        <div className="flex flex-col h-[400px] overflow-y-auto border border-gray-300 rounded p-4 bg-gray-50">
            {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-400">
                    Selecciona una conversación para ver los mensajes
                </div>
            ) : (
                <>
                    {messages.map((message) => (
                        <MessageBubble key={message.id} message={message} />
                    ))}
                    {loading && (
                        <div className="flex justify-start mb-3">
                            <div className="bg-white border border-gray-300 rounded px-4 py-2">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </>
            )}
        </div>
    )
}

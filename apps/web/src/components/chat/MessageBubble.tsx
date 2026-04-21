"use client"

import { useState } from "react"
import type { Message } from "@/types"
import { cn } from "@/lib/utils"

interface MessageBubbleProps {
    message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.sender === "user"

    return (
        <div
            className={cn(
                "flex w-full mb-3",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div
                className={cn(
                    "max-w-[70%] rounded-2xl px-4 py-3 text-sm font-bold shadow-soft transition-smooth",
                    isUser
                        ? "bg-gradient-to-r from-purple-600 to-purple-500 text-white"
                        : "bg-white dark:bg-gray-700 text-black dark:text-white border-2 border-gray-300 dark:border-gray-600"
                )}
            >
                <p className="whitespace-pre-wrap break-words">{message.message_text}</p>
                <span className="text-xs opacity-70 mt-1 block font-normal">
                    {new Date(message.created_at).toLocaleTimeString()}
                </span>
            </div>
        </div>
    )
}

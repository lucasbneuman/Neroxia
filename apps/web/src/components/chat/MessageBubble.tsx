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
                    "max-w-[70%] rounded px-4 py-2 text-sm",
                    isUser
                        ? "bg-black text-white"
                        : "bg-white text-black border border-gray-300"
                )}
            >
                <p className="whitespace-pre-wrap break-words">{message.message_text}</p>
                <span className="text-xs opacity-70 mt-1 block">
                    {new Date(message.created_at).toLocaleTimeString()}
                </span>
            </div>
        </div>
    )
}

"use client"

import { useState, useEffect } from "react"
import type { User, Message } from "@/types"
import { getMessages, getUserByPhone } from "@/lib/api"
import { ConversationList } from "@/components/chat/ConversationList"
import { ChatView } from "@/components/chat/ChatView"
import { UserDataPanel } from "@/components/chat/UserDataPanel"
import { HandoffControls } from "@/components/chat/HandoffControls"

export default function ChatsPage() {
    const [selectedPhone, setSelectedPhone] = useState<string | null>(null)
    const [selectedUser, setSelectedUser] = useState<User | null>(null)
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)

    const loadConversation = async (phone: string) => {
        setLoading(true)
        try {
            const [user, msgs] = await Promise.all([
                getUserByPhone(phone),
                getMessages(phone)
            ])
            setSelectedUser(user)
            setMessages(msgs)
            setSelectedPhone(phone)
        } catch (error) {
            console.error("Error loading conversation:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleSelectConversation = (phone: string) => {
        loadConversation(phone)
    }

    const handleModeChange = () => {
        // Reload user data after mode change
        if (selectedPhone) {
            loadConversation(selectedPhone)
        }
    }

    const handleMessageSent = () => {
        // Reload messages after sending
        if (selectedPhone) {
            loadConversation(selectedPhone)
        }
    }

    return (
        <div className="h-full p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-black dark:text-white">💬 Chats</h1>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Gestiona conversaciones en tiempo real
                </p>
            </div>

            <div className="grid grid-cols-12 gap-6 h-[calc(100vh-200px)]">
                {/* Left Column: Conversation List */}
                <div className="col-span-3 border border-gray-300 dark:border-gray-700 rounded overflow-hidden bg-white dark:bg-gray-800">
                    <ConversationList
                        onSelectConversation={handleSelectConversation}
                        selectedPhone={selectedPhone}
                        autoRefresh={true}
                    />
                </div>

                {/* Middle Column: Chat View with Input */}
                <div className="col-span-6 border border-gray-300 dark:border-gray-700 rounded overflow-hidden">
                    {selectedPhone && selectedUser ? (
                        <ChatView
                            phone={selectedPhone}
                            messages={messages}
                            conversationMode={selectedUser.conversation_mode}
                            onMessageSent={handleMessageSent}
                        />
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-400 dark:text-gray-500 font-bold bg-white dark:bg-gray-800">
                            Selecciona una conversación para ver los mensajes
                        </div>
                    )}
                </div>

                {/* Right Column: User Info + Handoff Controls */}
                <div className="col-span-3 flex flex-col space-y-4">
                    <UserDataPanel user={selectedUser} />
                    <HandoffControls
                        user={selectedUser}
                        onModeChange={handleModeChange}
                        onMessageSent={handleMessageSent}
                    />
                </div>
            </div>
        </div>
    )
}

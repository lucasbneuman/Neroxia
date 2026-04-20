"use client"

import { useState, useEffect } from "react"
import type { Message, CollectedData } from "@/types"
import { processTestMessage } from "@/lib/api"
import { TestChat } from "@/components/test/TestChat"
import { CollectedDataPanel } from "@/components/test/CollectedDataPanel"

const DEFAULT_DATA: CollectedData = {
    user_id: "USRPRUEBAS_00",
    name: "Aún no mencionó su nombre",
    email: "No proporcionado",
    phone: "+1234567890",
    last_contact: "-",
    intent: "-",
    sentiment: "-",
    stage: "-",
    needs: "-",
    requests_human: "No",
    notes: "-",
}

const STORAGE_KEYS = {
    MESSAGES: "test_chat_messages",
    DATA: "test_chat_data",
}

export default function TestPage() {
    const [messages, setMessages] = useState<Message[]>([])
    const [collectedData, setCollectedData] = useState<CollectedData>(DEFAULT_DATA)
    const [loading, setLoading] = useState(false)

    // Load persisted data on mount
    useEffect(() => {
        const savedMessages = localStorage.getItem(STORAGE_KEYS.MESSAGES)
        const savedData = localStorage.getItem(STORAGE_KEYS.DATA)

        if (savedMessages) {
            try {
                setMessages(JSON.parse(savedMessages))
            } catch (error) {
                console.error("Error loading saved messages:", error)
            }
        }

        if (savedData) {
            try {
                setCollectedData(JSON.parse(savedData))
            } catch (error) {
                console.error("Error loading saved data:", error)
            }
        }
    }, [])

    // Persist messages to localStorage
    useEffect(() => {
        if (messages.length > 0) {
            localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(messages))
        }
    }, [messages])

    // Persist collected data to localStorage
    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.DATA, JSON.stringify(collectedData))
    }, [collectedData])

    const handleSendMessage = async (message: string) => {
        // Add user message immediately
        const userMessage: Message = {
            id: messages.length + 1,
            user_id: 0,
            message_text: message,
            sender: "user",
            created_at: new Date().toISOString(),
        }

        setMessages([...messages, userMessage])
        setLoading(true)

        try {
            const result = await processTestMessage(
                collectedData.phone,
                message,
                messages
            )

            // Backend returns direct response object, not wrapped in APIResponse
            // Response format: { response: string, user_phone: string, user_name: string|null, ... }
            if (result && result.response) {
                // Add bot response
                const botMessage: Message = {
                    id: messages.length + 2,
                    user_id: 0,
                    message_text: result.response,
                    sender: "bot",
                    created_at: new Date().toISOString(),
                }

                setMessages((prev) => [...prev, botMessage])

                // Update collected data from response
                const updatedData: CollectedData = {
                    ...collectedData,
                    name: result.user_name || collectedData.name,
                    intent: result.intent_score?.toString() || collectedData.intent,
                    sentiment: result.sentiment || collectedData.sentiment,
                    stage: result.stage || collectedData.stage,
                }
                setCollectedData(updatedData)
            }
        } catch (error) {
            console.error("Error processing message:", error)
            // Add error message
            const errorMessage: Message = {
                id: messages.length + 2,
                user_id: 0,
                message_text: `Error: ${error instanceof Error ? error.message : "Error desconocido"}`,
                sender: "bot",
                created_at: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, errorMessage])
        } finally {
            setLoading(false)
        }
    }

    const handleClear = () => {
        setMessages([])
        setCollectedData(DEFAULT_DATA)
    }

    return (
        <div className="h-full p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-black dark:text-white">🧪 Pruebas</h1>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Prueba tu chatbot y observa los datos recolectados en tiempo real
                </p>
            </div>

            <div className="grid grid-cols-12 gap-6" style={{ height: "calc(100vh - 200px)" }}>
                {/* Left Column: Collected Data (narrower) */}
                <div className="col-span-3">
                    <CollectedDataPanel data={collectedData} />
                </div>

                {/* Right Column: Test Chat (wider) */}
                <div className="col-span-9">
                    <TestChat
                        messages={messages}
                        onSendMessage={handleSendMessage}
                        onClear={handleClear}
                        loading={loading}
                    />
                </div>
            </div>
        </div>
    )
}

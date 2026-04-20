"use client"

import { useState } from "react"
import type { User } from "@/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { takeControlByUserId, returnToBotByUserId, sendManualMessageByUserId } from "@/lib/api"

interface HandoffControlsProps {
    user: User | null
    onModeChange: () => void
    onMessageSent: () => void
}

export function HandoffControls({ user, onModeChange, onMessageSent }: HandoffControlsProps) {
    const [message, setMessage] = useState("")
    const [status, setStatus] = useState("")
    const [sending, setSending] = useState(false)
    const [toggling, setToggling] = useState(false)

    if (!user) {
        return null
    }

    const isManualMode = user.conversation_mode === "MANUAL"

    const handleToggleMode = async () => {
        setToggling(true)
        setStatus("")

        try {
            if (isManualMode) {
                await returnToBotByUserId(user.id)
                setStatus("🟢 Modo AUTO activado - El bot responderá automáticamente")
            } else {
                await takeControlByUserId(user.id)
                setStatus("🔴 Modo MANUAL activado - El bot no responderá")
            }
            onModeChange()
        } catch (error) {
            setStatus(`❌ Error: ${error instanceof Error ? error.message : "Error desconocido"}`)
        } finally {
            setToggling(false)
        }
    }

    const handleSendMessage = async () => {
        if (!message.trim()) {
            setStatus("⚠️ Por favor ingresa un mensaje")
            return
        }

        setSending(true)
        setStatus("")

        try {
            await sendManualMessageByUserId(user.id, message)
            setStatus("✅ Mensaje enviado")
            setMessage("")
            onMessageSent()
        } catch (error) {
            setStatus(`❌ Error: ${error instanceof Error ? error.message : "Error desconocido"}`)
        } finally {
            setSending(false)
        }
    }

    return (
        <div className="space-y-3">
            <Button
                onClick={handleToggleMode}
                disabled={toggling}
                variant="secondary"
                className="w-full"
            >
                {toggling ? "Cambiando..." : "🔄 Cambiar Modo (AUTO/MANUAL)"}
            </Button>

            {status && (
                <div className="p-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-800">
                    {status}
                </div>
            )}

            <div className="border-t border-gray-300 pt-3">
                <h4 className="text-sm font-semibold mb-2 text-black dark:text-white">Mensaje Manual</h4>
                <div className="flex gap-2">
                    <Input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder={isManualMode ? "Escribe un mensaje..." : "Solo disponible en modo MANUAL"}
                        disabled={!isManualMode || sending}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault()
                                handleSendMessage()
                            }
                        }}
                        className="flex-1"
                    />
                    <Button
                        onClick={handleSendMessage}
                        disabled={!isManualMode || sending || !message.trim()}
                        variant="primary"
                    >
                        {sending ? "Enviando..." : "Enviar"}
                    </Button>
                </div>
            </div>
        </div>
    )
}

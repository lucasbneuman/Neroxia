"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { previewVoice } from "@/lib/api"

interface VoiceSelectorProps {
    value: string
    onChange: (voice: string) => void
}

const voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

export function VoiceSelector({ value, onChange }: VoiceSelectorProps) {
    const [previewing, setPreviewing] = useState(false)
    const [audioUrl, setAudioUrl] = useState<string | null>(null)

    const handlePreview = async () => {
        setPreviewing(true)
        try {
            const audioBlob = await previewVoice(value)
            const url = URL.createObjectURL(audioBlob)
            setAudioUrl(url)

            // Auto-play
            const audio = new Audio(url)
            audio.play()
        } catch (error) {
            console.error("Error previewing voice:", error)
        } finally {
            setPreviewing(false)
        }
    }

    return (
        <div className="space-y-3">
            <label className="text-sm font-medium text-black dark:text-white">Voz TTS</label>
            <div className="grid grid-cols-3 gap-2">
                {voices.map((voice) => (
                    <button
                        key={voice}
                        type="button"
                        onClick={() => onChange(voice)}
                        className={`px-3 py-2 text-sm rounded border transition-colors ${value === voice
                            ? "bg-black text-white border-black"
                            : "bg-white text-black border-gray-300 hover:border-black"
                            }`}
                    >
                        {voice}
                    </button>
                ))}
            </div>
            <Button
                type="button"
                onClick={handlePreview}
                disabled={previewing}
                variant="secondary"
                size="sm"
            >
                {previewing ? "Generando..." : "🔊 Escuchar Voz"}
            </Button>
            <p className="text-xs text-gray-600">
                Selecciona la voz para mensajes de audio
            </p>
        </div>
    )
}

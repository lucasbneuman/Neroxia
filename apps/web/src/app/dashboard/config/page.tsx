"use client"

import { useState, useEffect } from "react"
import type { Config } from "@/types"
import { getConfig, saveConfig } from "@/lib/api"
import { useConfigStore } from "@/stores/config-store"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useToast } from "@/components/ui/toast"
import { VoiceSelector } from "@/components/config/VoiceSelector"
import { SliderControl } from "@/components/config/SliderControl"
import { FileUpload } from "@/components/config/FileUpload"

export default function ConfigPage() {
    const [activeTab, setActiveTab] = useState<"chatbot" | "product" | "knowledge">("chatbot")
    const { addToast } = useToast()

    // Use Zustand store for config state
    const { config, loading, saving, setConfig, updateConfig, setLoading, setSaving } = useConfigStore()

    useEffect(() => {
        loadConfig()
    }, [])

    const loadConfig = async () => {
        setLoading(true)
        try {
            const data = await getConfig()
            setConfig(data)
        } catch (error) {
            console.error("Error loading config:", error)
            addToast("Error al cargar configuración", "error")
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        setSaving(true)
        try {
            const result = await saveConfig(config)
            // API returns { status: "success", message: "...", configs: {...} }
            if (result.status === "success") {
                // Update the config state with the saved values from the API
                if (result.configs) {
                    setConfig(result.configs)
                }
                addToast("✅ Configuración guardada exitosamente", "success")
            } else {
                addToast(`Error: ${result.message || "Error desconocido"}`, "error")
            }
        } catch (error) {
            addToast(`Error: ${error instanceof Error ? error.message : "Error desconocido"}`, "error")
        } finally {
            setSaving(false)
        }
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-4">
                <LoadingSpinner size="lg" variant="accent" />
                <p className="text-gray-600 font-bold">Cargando configuración...</p>
            </div>
        )
    }

    return (
        <div className="h-full p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-black text-black dark:text-white tracking-tight">⚙️ Configuración</h1>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-2 font-bold">
                    Configura tu chatbot y describe tu producto/servicio
                </p>
            </div>

            {/* Tabs */}
            <div className="flex border-b-2 border-gray-200 mb-6">
                <button
                    onClick={() => setActiveTab("chatbot")}
                    className={`px-6 py-3 text-sm font-bold transition-smooth relative ${activeTab === "chatbot"
                        ? "text-purple-600"
                        : "text-gray-600 hover:text-purple-600"
                        }`}
                >
                    🤖 Chatbot
                    {activeTab === "chatbot" && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-purple-500 rounded-t-full" />
                    )}
                </button>
                <button
                    onClick={() => setActiveTab("product")}
                    className={`px-6 py-3 text-sm font-bold transition-smooth relative ${activeTab === "product"
                        ? "text-purple-600"
                        : "text-gray-600 hover:text-purple-600"
                        }`}
                >
                    📦 Producto/Servicio
                    {activeTab === "product" && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-purple-500 rounded-t-full" />
                    )}
                </button>
                <button
                    onClick={() => setActiveTab("knowledge")}
                    className={`px-6 py-3 text-sm font-bold transition-smooth relative ${activeTab === "knowledge"
                        ? "text-purple-600"
                        : "text-gray-600 hover:text-purple-600"
                        }`}
                >
                    📚 Base de Conocimientos
                    {activeTab === "knowledge" && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-purple-500 rounded-t-full" />
                    )}
                </button>
            </div>

            {/* Tab Content */}
            <div className="max-w-4xl">
                {activeTab === "chatbot" && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-semibold text-black dark:text-white">Configuración del Chatbot</h2>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                System Prompt
                            </label>
                            <Textarea
                                value={config.system_prompt || ""}
                                onChange={(e) => updateConfig({ system_prompt: e.target.value })}
                                placeholder="Eres un asistente de ventas profesional..."
                                rows={4}
                            />
                            <p className="text-xs text-gray-600 mt-1">
                                Personalidad y comportamiento base del chatbot
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Mensaje de Bienvenida
                            </label>
                            <Textarea
                                value={config.welcome_message || ""}
                                onChange={(e) => updateConfig({ welcome_message: e.target.value })}
                                placeholder="¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
                                rows={2}
                            />
                            <p className="text-xs text-gray-600 mt-1">
                                Primer mensaje que verá el usuario al iniciar la conversación
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Link de Pago
                            </label>
                            <Input
                                value={config.payment_link || ""}
                                onChange={(e) => updateConfig({ payment_link: e.target.value })}
                                placeholder="https://tu-sitio.com/pagar"
                            />
                            <p className="text-xs text-gray-600 mt-1">
                                URL donde los clientes pueden realizar el pago
                            </p>
                        </div>

                        <div className="border-t border-gray-300 dark:border-gray-700 pt-6">
                            <h3 className="text-base font-semibold text-black dark:text-white mb-4">Comportamiento</h3>

                            <div className="grid grid-cols-2 gap-6">
                                <SliderControl
                                    label="Delay de Respuesta"
                                    value={config.response_delay_minutes || 0.5}
                                    onChange={(value) => updateConfig({ response_delay_minutes: value })}
                                    min={0}
                                    max={10}
                                    step={0.1}
                                    unit=" min"
                                    info="Tiempo de espera antes de responder"
                                />

                                <SliderControl
                                    label="Máximo de Palabras por Respuesta"
                                    value={config.max_words_per_response || 100}
                                    onChange={(value) => updateConfig({ max_words_per_response: value })}
                                    min={5}
                                    max={500}
                                    step={5}
                                    info="Límite de palabras en cada mensaje"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-6 mt-6">
                                <div className="flex items-center space-x-2">
                                    <Checkbox
                                        checked={config.use_emojis}
                                        onCheckedChange={(checked) =>
                                            updateConfig({ use_emojis: checked as boolean })
                                        }
                                    />
                                    <label className="text-sm text-black dark:text-white">Usar Emojis</label>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Checkbox
                                        checked={config.multi_part_messages}
                                        onCheckedChange={(checked) =>
                                            updateConfig({ multi_part_messages: checked as boolean })
                                        }
                                    />
                                    <label className="text-sm text-black dark:text-white">Mensajes en Múltiples Partes</label>
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-gray-300 dark:border-gray-700 pt-6">
                            <h3 className="text-base font-semibold text-black dark:text-white mb-4">Audio/TTS</h3>

                            <SliderControl
                                label="Ratio Texto/Audio"
                                value={config.text_audio_ratio || 0}
                                onChange={(value) => updateConfig({ text_audio_ratio: value })}
                                min={0}
                                max={100}
                                step={10}
                                unit="%"
                                info="0% = solo texto, 100% = solo audio"
                            />

                            <div className="mt-6">
                                <VoiceSelector
                                    value={config.tts_voice || "nova"}
                                    onChange={(voice) => updateConfig({ tts_voice: voice as any })}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "product" && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-semibold text-black dark:text-white">Información de tu Producto/Servicio</h2>
                        <p className="text-sm text-gray-600">
                            Esta información se usará para adaptar las respuestas del chatbot
                        </p>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Nombre del Producto/Servicio
                            </label>
                            <Input
                                value={config.product_name || ""}
                                onChange={(e) => updateConfig({ product_name: e.target.value })}
                                placeholder="Ej: Curso de Marketing Digital"
                            />
                            <p className="text-xs text-gray-600 mt-1">¿Qué vendes?</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Descripción
                            </label>
                            <Textarea
                                value={config.product_description || ""}
                                onChange={(e) => updateConfig({ product_description: e.target.value })}
                                placeholder="Curso completo de marketing digital con más de 50 horas de contenido..."
                                rows={4}
                            />
                            <p className="text-xs text-gray-600 mt-1">Descripción general de lo que ofreces</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Características Principales
                            </label>
                            <Textarea
                                value={config.product_features || ""}
                                onChange={(e) => updateConfig({ product_features: e.target.value })}
                                placeholder="- 50+ horas de video&#10;- Certificado al finalizar&#10;- Acceso de por vida&#10;- Soporte 24/7"
                                rows={5}
                            />
                            <p className="text-xs text-gray-600 mt-1">Lista las características clave (una por línea)</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                Beneficios para el Cliente
                            </label>
                            <Textarea
                                value={config.product_benefits || ""}
                                onChange={(e) => updateConfig({ product_benefits: e.target.value })}
                                placeholder="- Aprenderás a crear campañas efectivas&#10;- Aumentarás tus ventas online&#10;- Dominarás las redes sociales"
                                rows={5}
                            />
                            <p className="text-xs text-gray-600 mt-1">¿Qué gana el cliente? (una por línea)</p>
                        </div>

                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                    Precio
                                </label>
                                <Input
                                    value={config.product_price || ""}
                                    onChange={(e) => updateConfig({ product_price: e.target.value })}
                                    placeholder="Ej: $99 USD, Desde $50, Consultar"
                                />
                                <p className="text-xs text-gray-600 mt-1">Precio o rango de precio (opcional)</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-black dark:text-white mb-2">
                                    Público Objetivo
                                </label>
                                <Input
                                    value={config.product_target_audience || ""}
                                    onChange={(e) => updateConfig({ product_target_audience: e.target.value })}
                                    placeholder="Ej: Emprendedores, Pequeños negocios"
                                />
                                <p className="text-xs text-gray-600 mt-1">¿A quién está dirigido?</p>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "knowledge" && (
                    <FileUpload />
                )}
            </div>

            {/* Save Button (only for chatbot and product tabs) */}
            {activeTab !== "knowledge" && (
                <div className="mt-8 border-t border-gray-300 pt-6">
                    <Button
                        onClick={handleSave}
                        disabled={saving}
                        variant="primary"
                        size="lg"
                    >
                        {saving ? (
                            <span className="flex items-center justify-center gap-2">
                                <LoadingSpinner size="sm" variant="default" />
                                Guardando...
                            </span>
                        ) : (
                            "💾 Guardar Configuración"
                        )}
                    </Button>
                </div>
            )}
        </div>
    )
}

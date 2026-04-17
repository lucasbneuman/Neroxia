"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { uploadRAGDocuments, clearRAGCollection, getRAGStats } from "@/lib/api"
import type { RAGStats } from "@/types"

export function FileUpload() {
    const [uploading, setUploading] = useState(false)
    const [uploadStatus, setUploadStatus] = useState("")
    const [stats, setStats] = useState<RAGStats>({ total_chunks: 0 })
    const [clearing, setClearing] = useState(false)

    const loadStats = async () => {
        try {
            const data = await getRAGStats()
            setStats(data)
        } catch (error) {
            console.error("Error loading RAG stats:", error)
        }
    }

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        setUploading(true)
        setUploadStatus("")

        try {
            const fileArray = Array.from(files)
            const result = await uploadRAGDocuments(fileArray)

            if (result.status === "success") {
                setUploadStatus(
                    `✅ ${result.uploaded} archivo(s) subido(s) correctamente (${result.total_chunks} fragmentos)`
                )
                await loadStats()
            } else {
                setUploadStatus(`❌ Error: ${result.error || result.message || "Error desconocido"}`)
            }
        } catch (error) {
            setUploadStatus(`❌ Error: ${error instanceof Error ? error.message : "Error desconocido"}`)
        } finally {
            setUploading(false)
            // Reset file input
            e.target.value = ""
        }
    }

    const handleClearCollection = async () => {
        if (!confirm("¿Estás seguro de que quieres eliminar todos los documentos?")) {
            return
        }

        setClearing(true)
        setUploadStatus("")

        try {
            const result = await clearRAGCollection()
            if (result.status === "success") {
                setUploadStatus("✅ Base de conocimientos limpiada exitosamente")
                await loadStats()
            } else {
                setUploadStatus(`❌ Error: ${result.error || result.message || "Error desconocido"}`)
            }
        } catch (error) {
            setUploadStatus(`❌ Error: ${error instanceof Error ? error.message : "Error desconocido"}`)
        } finally {
            setClearing(false)
        }
    }

    // Load stats on mount
    useState(() => {
        loadStats()
    })

    return (
        <div className="space-y-4">
            <div>
                <h3 className="text-lg font-semibold mb-2 text-black dark:text-white">
                    📚 Base de Conocimientos
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                    Sube archivos con información sobre tu producto/servicio. El chatbot usará esta información para responder preguntas específicas.
                </p>
            </div>

            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-3">
                    <p className="text-sm font-medium text-black dark:text-white">Formatos soportados: TXT, PDF, DOC, DOCX</p>

                    <div className="border-2 border-dashed border-gray-300 rounded p-6 text-center">
                        <input
                            type="file"
                            id="file-upload"
                            multiple
                            accept=".txt,.pdf,.doc,.docx"
                            onChange={handleFileUpload}
                            disabled={uploading}
                            className="hidden"
                        />
                        <label
                            htmlFor="file-upload"
                            className="cursor-pointer inline-block"
                        >
                            <div className="text-4xl mb-2">📤</div>
                            <p className="text-sm text-gray-600">
                                {uploading ? "Subiendo..." : "Click para seleccionar archivos"}
                            </p>
                        </label>
                    </div>

                    <div className="p-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-sm">
                        📊 Fragmentos en base de datos: <strong>{stats.total_chunks}</strong>
                    </div>

                    {uploadStatus && (
                        <div className="p-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-sm">
                            {uploadStatus}
                        </div>
                    )}
                </div>

                <div className="space-y-3">
                    <p className="text-sm font-semibold text-black dark:text-white">ℹ️ Información</p>
                    <div className="text-sm text-gray-700 space-y-2">
                        <p><strong>¿Qué puedes subir?</strong></p>
                        <ul className="list-disc list-inside space-y-1 text-xs">
                            <li>Catálogos de productos</li>
                            <li>Manuales de usuario</li>
                            <li>FAQs</li>
                            <li>Guías de precios</li>
                            <li>Políticas y términos</li>
                        </ul>

                        <p className="mt-3"><strong>¿Cómo funciona?</strong></p>
                        <ol className="list-decimal list-inside space-y-1 text-xs">
                            <li>Sube tus documentos</li>
                            <li>El sistema los procesa automáticamente</li>
                            <li>El bot usa esta información para responder</li>
                        </ol>
                    </div>
                </div>
            </div>

            <div className="border-t border-gray-300 pt-4">
                <p className="text-sm font-semibold text-black dark:text-white mb-2">⚠️ Zona de Peligro</p>
                <Button
                    onClick={handleClearCollection}
                    disabled={clearing}
                    variant="danger"
                    size="sm"
                >
                    {clearing ? "Limpiando..." : "🗑️ Limpiar Base de Conocimientos"}
                </Button>
            </div>
        </div>
    )
}

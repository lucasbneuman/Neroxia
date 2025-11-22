"use client"

import type { CollectedData } from "@/types"

interface CollectedDataPanelProps {
    data: CollectedData
}

export function CollectedDataPanel({ data }: CollectedDataPanelProps) {
    return (
        <div className="space-y-2">
            <h2 className="text-lg font-semibold text-black mb-4">👤 Datos Recolectados</h2>

            <div className="space-y-1 text-sm">
                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">🆔 ID: {data.user_id}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">📝 Nombre: {data.name}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">📧 Email: {data.email}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">📱 Teléfono: {data.phone}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">🕐 Último contacto: {data.last_contact}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">🎯 Intención: {data.intent}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">😊 Sentimiento: {data.sentiment}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">📊 Etapa: {data.stage}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">💡 Necesidades: {data.needs}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <span className="text-black">👨‍💼 Solicita Humano: {data.requests_human}</span>
                </div>

                <div className="p-2 bg-white border border-gray-300 rounded">
                    <div className="text-black">
                        <div className="font-medium mb-1">📋 Notas:</div>
                        <div className="text-xs text-gray-700 whitespace-pre-wrap">{data.notes}</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

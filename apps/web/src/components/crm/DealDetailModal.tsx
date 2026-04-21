"use client"

import { useState, useEffect } from "react"
import { X, Phone, Mail, Calendar, DollarSign, TrendingUp, Save, Edit2, Plus, Trash2, Tag as TagIcon, StickyNote } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    updateDeal,
    getNotes,
    createNote,
    deleteNote,
    getTags,
    getUserTags,
    addTagToUser,
    removeTagFromUser
} from "@/lib/api"
import type { Deal, Note, Tag } from "@/types"
import { cn } from "@/lib/utils"

interface DealDetailModalProps {
    deal: Deal | null
    isOpen: boolean
    onClose: () => void
}

const STAGE_LABELS: Record<string, string> = {
    new_lead: "Nuevo Lead",
    qualified: "Calificado",
    in_conversation: "En Conversación",
    proposal_sent: "Propuesta Enviada",
    won: "Ganado",
    lost: "Perdido",
}

const STAGE_COLORS: Record<string, string> = {
    new_lead: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    qualified: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    in_conversation: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    proposal_sent: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
    won: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    lost: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
}

export function DealDetailModal({ deal, isOpen, onClose }: DealDetailModalProps) {
    const [isEditing, setIsEditing] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [formData, setFormData] = useState<Partial<Deal>>({})

    // Notes & Tags State
    const [notes, setNotes] = useState<Note[]>([])
    const [userTags, setUserTags] = useState<Tag[]>([])
    const [availableTags, setAvailableTags] = useState<Tag[]>([])
    const [newNote, setNewNote] = useState("")
    const [isAddingNote, setIsAddingNote] = useState(false)
    const [showTagSelector, setShowTagSelector] = useState(false)

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden"
            setIsEditing(false)
            if (deal) {
                setFormData({
                    title: deal.title,
                    value: deal.value,
                    stage: deal.stage,
                    probability: deal.probability,
                    expected_close_date: deal.expected_close_date
                })
                loadNotesAndTags(deal.user_id)
            }
        } else {
            document.body.style.overflow = "unset"
        }
        return () => {
            document.body.style.overflow = "unset"
        }
    }, [isOpen, deal])

    const loadNotesAndTags = async (userId: number) => {
        try {
            const [fetchedNotes, fetchedUserTags, allTags] = await Promise.all([
                getNotes(userId),
                getUserTags(userId),
                getTags()
            ])
            setNotes(fetchedNotes)
            setUserTags(fetchedUserTags)
            setAvailableTags(allTags)
        } catch (error) {
            console.error("Error loading notes/tags:", error)
        }
    }

    const handleSave = async () => {
        if (!deal) return
        setIsSaving(true)
        try {
            await updateDeal(deal.id, formData)
            setIsEditing(false)
            onClose() // Close to refresh parent
        } catch (error) {
            console.error("Error updating deal:", error)
            alert("Error al actualizar el deal")
        } finally {
            setIsSaving(false)
        }
    }

    const handleAddNote = async () => {
        if (!deal || !newNote.trim()) return
        setIsAddingNote(true)
        try {
            const note = await createNote(deal.user_id, newNote, "00000000-0000-0000-0000-000000000000", deal.id)
            setNotes([note, ...notes])
            setNewNote("")
        } catch (error) {
            console.error("Error adding note:", error)
        } finally {
            setIsAddingNote(false)
        }
    }

    const handleDeleteNote = async (noteId: number) => {
        try {
            await deleteNote(noteId)
            setNotes(notes.filter(n => n.id !== noteId))
        } catch (error) {
            console.error("Error deleting note:", error)
        }
    }

    const handleAddTag = async (tagId: number) => {
        if (!deal) return
        try {
            await addTagToUser(deal.user_id, tagId)
            const tagToAdd = availableTags.find(t => t.id === tagId)
            if (tagToAdd) {
                setUserTags([...userTags, tagToAdd])
            }
            setShowTagSelector(false)
        } catch (error) {
            console.error("Error adding tag:", error)
        }
    }

    const handleRemoveTag = async (tagId: number) => {
        if (!deal) return
        try {
            await removeTagFromUser(deal.user_id, tagId)
            setUserTags(userTags.filter(t => t.id !== tagId))
        } catch (error) {
            console.error("Error removing tag:", error)
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("es-ES", {
            day: "2-digit",
            month: "long",
            year: "numeric"
        })
    }

    if (!isOpen || !deal) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-800">
                {/* Header */}
                <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-6 flex items-start justify-between z-10">
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            {isEditing ? (
                                <input
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    className="text-2xl font-black text-black dark:text-white bg-transparent border-b-2 border-purple-500 focus:outline-none w-full"
                                    placeholder="Título del deal"
                                />
                            ) : (
                                <h2 className="text-2xl font-black text-black dark:text-white">
                                    {deal.title}
                                </h2>
                            )}
                            {deal.source === "test" && (
                                <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-sm font-bold rounded-full whitespace-nowrap">
                                    TEST
                                </span>
                            )}
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                            {isEditing ? (
                                <select
                                    value={formData.stage}
                                    onChange={(e) => setFormData({ ...formData, stage: e.target.value as Deal['stage'] })}
                                    className="px-3 py-1 rounded-full text-xs font-bold bg-gray-100 dark:bg-gray-800 border-none focus:ring-2 focus:ring-purple-500"
                                >
                                    {Object.entries(STAGE_LABELS).map(([key, label]) => (
                                        <option key={key} value={key}>{label}</option>
                                    ))}
                                </select>
                            ) : (
                                <span className={cn(
                                    "inline-block px-3 py-1 rounded-full text-xs font-bold",
                                    STAGE_COLORS[deal.stage] || "bg-gray-100 text-gray-700"
                                )}>
                                    {STAGE_LABELS[deal.stage] || deal.stage}
                                </span>
                            )}

                            {/* Tags Display */}
                            {userTags.map(tag => (
                                <span
                                    key={tag.id}
                                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
                                    style={{ borderColor: tag.color, color: tag.color }}
                                >
                                    {tag.name}
                                    <button
                                        onClick={() => handleRemoveTag(tag.id)}
                                        className="ml-1 hover:text-red-500"
                                    >
                                        <X size={12} />
                                    </button>
                                </span>
                            ))}

                            <div className="relative">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
                                    onClick={() => setShowTagSelector(!showTagSelector)}
                                >
                                    <Plus size={14} />
                                </Button>
                                {showTagSelector && (
                                    <div className="absolute top-full left-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-2 z-20">
                                        <p className="text-xs font-bold text-gray-500 mb-2 px-2">Agregar Etiqueta</p>
                                        {availableTags.filter(t => !userTags.find(ut => ut.id === t.id)).map(tag => (
                                            <button
                                                key={tag.id}
                                                onClick={() => handleAddTag(tag.id)}
                                                className="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                            >
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: tag.color }} />
                                                {tag.name}
                                            </button>
                                        ))}
                                        {availableTags.length === 0 && (
                                            <p className="text-xs text-gray-400 px-2">No hay etiquetas disponibles</p>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onClose}
                        className="hover:bg-gray-100 dark:hover:bg-gray-800"
                    >
                        <X size={20} />
                    </Button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Deal Info */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                                <DollarSign size={16} />
                                <span className="text-xs font-bold uppercase">Valor</span>
                            </div>
                            {isEditing ? (
                                <input
                                    type="number"
                                    value={formData.value}
                                    onChange={(e) => setFormData({ ...formData, value: parseFloat(e.target.value) })}
                                    className="text-2xl font-black text-black dark:text-white bg-transparent border-b border-purple-500 focus:outline-none w-full"
                                />
                            ) : (
                                <p className="text-2xl font-black text-black dark:text-white">
                                    ${deal.value.toLocaleString()}
                                </p>
                            )}
                            <p className="text-xs text-gray-500 mt-1">{deal.currency}</p>
                        </div>

                        <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                                <TrendingUp size={16} />
                                <span className="text-xs font-bold uppercase">Probabilidad</span>
                            </div>
                            {isEditing ? (
                                <div className="flex items-center gap-2">
                                    <input
                                        type="number"
                                        value={formData.probability}
                                        onChange={(e) => setFormData({ ...formData, probability: parseInt(e.target.value) })}
                                        className="text-2xl font-black text-black dark:text-white bg-transparent border-b border-purple-500 focus:outline-none w-full"
                                        min="0"
                                        max="100"
                                    />
                                    <span className="text-xl font-bold">%</span>
                                </div>
                            ) : (
                                <p className="text-2xl font-black text-black dark:text-white">
                                    {deal.probability}%
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Contact Info */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase mb-3">
                            Información de Contacto
                        </h3>
                        <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold text-lg">
                                    {deal.user?.name?.charAt(0) || deal.user?.phone?.charAt(1) || "?"}
                                </div>
                                <div>
                                    <p className="font-bold text-black dark:text-white">
                                        {deal.user?.name || "Sin nombre"}
                                    </p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        {deal.user?.stage || "Sin etapa"}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                <Phone size={16} />
                                <span>{deal.user?.phone}</span>
                            </div>

                            {deal.user?.email && (
                                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                    <Mail size={16} />
                                    <span>{deal.user.email}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Timeline */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase mb-3">
                            Timeline
                        </h3>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                                <Calendar size={14} className="text-gray-400" />
                                <span className="text-gray-600 dark:text-gray-400">Creado:</span>
                                <span className="font-medium text-black dark:text-white">
                                    {formatDate(deal.created_at)}
                                </span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Calendar size={14} className="text-gray-400" />
                                <span className="text-gray-600 dark:text-gray-400">Última actualización:</span>
                                <span className="font-medium text-black dark:text-white">
                                    {formatDate(deal.updated_at)}
                                </span>
                            </div>

                            <div className="flex items-center gap-2 text-sm">
                                <Calendar size={14} className="text-gray-400" />
                                <span className="text-gray-600 dark:text-gray-400">Cierre esperado:</span>
                                {isEditing ? (
                                    <input
                                        type="date"
                                        value={formData.expected_close_date ? new Date(formData.expected_close_date).toISOString().split('T')[0] : ''}
                                        onChange={(e) => setFormData({ ...formData, expected_close_date: e.target.value ? new Date(e.target.value).toISOString() : undefined })}
                                        className="font-medium text-black dark:text-white bg-transparent border-b border-purple-500 focus:outline-none"
                                    />
                                ) : (
                                    <span className="font-medium text-black dark:text-white">
                                        {deal.expected_close_date ? formatDate(deal.expected_close_date) : "No definido"}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Notes Section */}
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase">
                                Notas
                            </h3>
                        </div>

                        <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl space-y-4">
                            {/* Add Note Input */}
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={newNote}
                                    onChange={(e) => setNewNote(e.target.value)}
                                    placeholder="Agregar una nota..."
                                    className="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder:text-gray-400"
                                    onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
                                />
                                <Button
                                    size="sm"
                                    onClick={handleAddNote}
                                    disabled={!newNote.trim() || isAddingNote}
                                >
                                    <Plus size={16} />
                                </Button>
                            </div>

                            {/* Notes List */}
                            <div className="space-y-3 max-h-[200px] overflow-y-auto">
                                {notes.length === 0 ? (
                                    <p className="text-center text-sm text-gray-400 py-2">No hay notas todavía</p>
                                ) : (
                                    notes.map(note => (
                                        <div key={note.id} className="bg-white dark:bg-gray-900 p-3 rounded-lg border border-gray-100 dark:border-gray-800 group relative">
                                            <p className="text-sm text-gray-700 dark:text-gray-200 pr-6">{note.content}</p>
                                            <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                                                <span>{formatDate(note.created_at)}</span>
                                                <span>{note.created_by === '00000000-0000-0000-0000-000000000000' ? 'Sistema' : 'Usuario'}</span>
                                            </div>
                                            <button
                                                onClick={() => handleDeleteNote(note.id)}
                                                className="absolute top-2 right-2 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 p-6 flex gap-3">
                    {isEditing ? (
                        <>
                            <Button
                                variant="outline"
                                className="flex-1"
                                onClick={() => setIsEditing(false)}
                                disabled={isSaving}
                            >
                                Cancelar
                            </Button>
                            <Button
                                variant="primary"
                                className="flex-1 gap-2"
                                onClick={handleSave}
                                disabled={isSaving}
                            >
                                {isSaving ? (
                                    <>Guardando...</>
                                ) : (
                                    <>
                                        <Save size={16} />
                                        Guardar Cambios
                                    </>
                                )}
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button variant="outline" className="flex-1" onClick={onClose}>
                                Cerrar
                            </Button>
                            <Button
                                variant="primary"
                                className="flex-1 gap-2"
                                onClick={() => setIsEditing(true)}
                            >
                                <Edit2 size={16} />
                                Editar Deal
                            </Button>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

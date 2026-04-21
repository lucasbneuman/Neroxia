'use client'

import * as React from "react"
import { cn } from "@/lib/utils"
import { X, CheckCircle, AlertCircle, Info } from "lucide-react"

export type ToastType = "success" | "error" | "info" | "loading"

export interface Toast {
    id: string
    type: ToastType
    message: string
    duration?: number
}

interface ToastContextValue {
    toasts: Toast[]
    addToast: (message: string, type: ToastType, duration?: number) => string
    removeToast: (id: string) => void
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = React.useState<Toast[]>([])

    const addToast = React.useCallback((message: string, type: ToastType, duration: number = 3000) => {
        const id = Math.random().toString(36).substr(2, 9)
        setToasts((prev) => [...prev, { id, message, type, duration }])

        if (type !== "loading" && duration > 0) {
            setTimeout(() => {
                removeToast(id)
            }, duration)
        }

        return id
    }, [])

    const removeToast = React.useCallback((id: string) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id))
    }, [])

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
            {children}
            <ToastContainer toasts={toasts} onRemove={removeToast} />
        </ToastContext.Provider>
    )
}

export function useToast() {
    const context = React.useContext(ToastContext)
    if (!context) {
        throw new Error("useToast must be used within ToastProvider")
    }
    return context
}

function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: string) => void }) {
    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
            {toasts.map((toast) => (
                <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
            ))}
        </div>
    )
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
    const icons = {
        success: <CheckCircle className="h-5 w-5 text-green-600" />,
        error: <AlertCircle className="h-5 w-5 text-red-600" />,
        info: <Info className="h-5 w-5 text-blue-600" />,
        loading: (
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-purple-600 border-t-transparent" />
        ),
    }

    const bgColors = {
        success: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
        error: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
        info: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
        loading: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800",
    }

    return (
        <div
            className={cn(
                "flex items-center gap-3 p-4 rounded-2xl border-2 shadow-medium animate-in slide-in-from-right-full",
                bgColors[toast.type]
            )}
            role="alert"
            aria-live="polite"
        >
            {icons[toast.type]}
            <p className="flex-1 text-sm font-bold text-gray-900 dark:text-white">
                {toast.message}
            </p>
            {toast.type !== "loading" && (
                <button
                    onClick={() => onRemove(toast.id)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-smooth"
                    aria-label="Close notification"
                >
                    <X className="h-4 w-4" />
                </button>
            )}
        </div>
    )
}

// Helper functions for easier usage
export const toast = {
    success: (message: string, duration?: number) => {
        // This will be called from components using useToast hook
        return { message, type: "success" as ToastType, duration }
    },
    error: (message: string, duration?: number) => {
        return { message, type: "error" as ToastType, duration }
    },
    info: (message: string, duration?: number) => {
        return { message, type: "info" as ToastType, duration }
    },
    loading: (message: string) => {
        return { message, type: "loading" as ToastType, duration: 0 }
    },
}

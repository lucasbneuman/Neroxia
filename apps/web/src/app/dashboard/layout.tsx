"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuthStore } from "@/stores/auth-store"
import { MessageSquare, Settings, FlaskConical, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const pathname = usePathname()
    const { logout } = useAuthStore()

    useEffect(() => {
        // Check if user is authenticated
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("token")
            if (!token) {
                router.push("/login")
            }
        }
    }, [router])

    const handleLogout = () => {
        logout()
        router.push("/login")
    }

    const navItems = [
        {
            href: "/dashboard/chat",
            icon: MessageSquare,
            label: "💬 Chats",
            active: pathname?.startsWith("/dashboard/chat"),
        },
        {
            href: "/dashboard/config",
            icon: Settings,
            label: "⚙️ Configuración",
            active: pathname?.startsWith("/dashboard/config"),
        },
        {
            href: "/dashboard/test",
            icon: FlaskConical,
            label: "🧪 Pruebas",
            active: pathname?.startsWith("/dashboard/test"),
        },
    ]

    return (
        <div className="flex h-screen bg-white">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-300 flex flex-col">
                <div className="p-6 border-b border-gray-300">
                    <h1 className="text-xl font-bold text-black">WhatsApp Sales Bot</h1>
                    <p className="text-xs text-gray-600 mt-1">Panel de Control</p>
                </div>

                <nav className="flex-1 p-4">
                    <div className="space-y-1">
                        {navItems.map((item) => (
                            <a
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 text-sm font-medium rounded transition-colors",
                                    item.active
                                        ? "bg-black text-white"
                                        : "text-gray-700 hover:bg-gray-100"
                                )}
                            >
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </a>
                        ))}
                    </div>
                </nav>

                <div className="p-4 border-t border-gray-300">
                    <Button
                        variant="secondary"
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2"
                    >
                        <LogOut size={18} />
                        <span>Cerrar Sesión</span>
                    </Button>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <main className="flex-1 overflow-auto">{children}</main>
            </div>
        </div>
    )
}

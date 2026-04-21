"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuthStore } from "@/stores/auth-store"
import { useUserStore } from "@/stores/user-store"
import { MessageSquare, Settings, FlaskConical, LogOut, BarChart3, User, CreditCard, Plug, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import { cn } from "@/lib/utils"
import { getUserProfile } from "@/lib/api"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const pathname = usePathname()
    const { logout } = useAuthStore()
    const { profile, setProfile } = useUserStore()
    const [userMenuOpen, setUserMenuOpen] = useState(false)

    useEffect(() => {
        // Check if user is authenticated
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("token")
            if (!token) {
                router.push("/login")
            } else {
                // Load user profile
                loadProfile()
            }
        }
    }, [router])

    const loadProfile = async () => {
        try {
            const data = await getUserProfile()
            setProfile(data)
        } catch (error) {
            console.error('Error loading profile:', error)
        }
    }

    const handleLogout = () => {
        logout()
        router.push("/login")
    }

    const navItems = [
        {
            href: "/dashboard/chat",
            icon: MessageSquare,
            label: "Chats",
            active: pathname?.startsWith("/dashboard/chat"),
        },
        {
            href: "/dashboard/crm",
            icon: BarChart3,
            label: "CRM",
            active: pathname?.startsWith("/dashboard/crm"),
        },
        {
            href: "/dashboard/config",
            icon: Settings,
            label: "Configuración Bot",
            active: pathname?.startsWith("/dashboard/config") && pathname === "/dashboard/config",
        },
        {
            href: "/dashboard/test",
            icon: FlaskConical,
            label: "Pruebas",
            active: pathname?.startsWith("/dashboard/test"),
        },
    ]

    const settingsItems = [
        {
            href: "/dashboard/profile",
            icon: User,
            label: "Mi Perfil",
            active: pathname?.startsWith("/dashboard/profile"),
        },
        {
            href: "/dashboard/integrations",
            icon: Plug,
            label: "Integraciones",
            active: pathname?.startsWith("/dashboard/integrations"),
        },
        {
            href: "/dashboard/subscription",
            icon: CreditCard,
            label: "Suscripción",
            active: pathname?.startsWith("/dashboard/subscription"),
        },
    ]

    return (
        <div className="flex h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-950 dark:to-gray-900">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col shadow-medium transition-colors">
                <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-black text-black dark:text-white tracking-tight">
                            Sales Oracle
                        </h1>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 font-bold">Panel de Control</p>
                    </div>
                    <ThemeToggle />
                </div>

                <nav className="flex-1 p-4 overflow-y-auto">
                    <div className="space-y-6">
                        {/* Main Navigation */}
                        <div className="space-y-2">
                            <p className="px-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                                Principal
                            </p>
                            {navItems.map((item) => (
                                <a
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-4 py-3 text-sm font-bold rounded-2xl transition-smooth",
                                        item.active
                                            ? "bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-accent"
                                            : "text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:text-purple-600 dark:hover:text-purple-400"
                                    )}
                                >
                                    <item.icon size={18} />
                                    <span>{item.label}</span>
                                </a>
                            ))}
                        </div>

                        {/* Settings Navigation */}
                        <div className="space-y-2">
                            <p className="px-4 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                                Configuración
                            </p>
                            {settingsItems.map((item) => (
                                <a
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-4 py-3 text-sm font-bold rounded-2xl transition-smooth",
                                        item.active
                                            ? "bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-accent"
                                            : "text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:text-purple-600 dark:hover:text-purple-400"
                                    )}
                                >
                                    <item.icon size={18} />
                                    <span>{item.label}</span>
                                </a>
                            ))}
                        </div>
                    </div>
                </nav>

                <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-3">
                    {/* User Profile Mini Card */}
                    {profile && (
                        <div className="px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold">
                                    {profile.company_name?.[0] || 'U'}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-bold text-gray-900 dark:text-white truncate">
                                        {profile.company_name || 'Usuario'}
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {profile.role === 'owner' ? 'Propietario' : 'Usuario'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    <Button
                        variant="secondary"
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2 rounded-2xl shadow-soft hover:shadow-medium transition-smooth"
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

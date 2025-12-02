"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Users, KanbanSquare } from "lucide-react"
import { cn } from "@/lib/utils"

export default function CrmLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname()

    const tabs = [
        {
            href: "/dashboard/crm/dashboard",
            label: "Dashboard",
            icon: LayoutDashboard,
            active: pathname?.includes("/dashboard/crm/dashboard"),
        },
        {
            href: "/dashboard/crm/contacts",
            label: "Contactos",
            icon: Users,
            active: pathname?.includes("/dashboard/crm/contacts"),
        },
        {
            href: "/dashboard/crm/pipeline",
            label: "Pipeline",
            icon: KanbanSquare,
            active: pathname?.includes("/dashboard/crm/pipeline"),
        },
    ]

    return (
        <div className="h-full flex flex-col p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-black text-black dark:text-white tracking-tight">💼 CRM</h1>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-2 font-bold">
                    Gestiona tus clientes y oportunidades de venta
                </p>
            </div>

            {/* Tabs */}
            <div className="flex border-b-2 border-gray-200 dark:border-gray-800 mb-6">
                {tabs.map((tab) => (
                    <Link
                        key={tab.href}
                        href={tab.href}
                        className={cn(
                            "px-6 py-3 text-sm font-bold transition-smooth relative flex items-center gap-2",
                            tab.active
                                ? "text-purple-600 dark:text-purple-400"
                                : "text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400"
                        )}
                    >
                        <tab.icon size={18} />
                        {tab.label}
                        {tab.active && (
                            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 to-purple-500 rounded-t-full" />
                        )}
                    </Link>
                ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto">
                {children}
            </div>
        </div>
    )
}

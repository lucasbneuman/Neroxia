'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { MessageSquare, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const { isAuthenticated, logout } = useAuthStore();

    useEffect(() => {
        // Check if user is authenticated
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('token');
            if (!token) {
                router.push('/login');
            }
        }
    }, [router]);

    const handleLogout = () => {
        logout();
        router.push('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md">
                <div className="p-4 border-b">
                    <h1 className="text-xl font-bold text-gray-800">WhatsApp Sales</h1>
                </div>

                <nav className="p-4">
                    <a
                        href="/dashboard/chat"
                        className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <MessageSquare size={20} />
                        <span>Conversations</span>
                    </a>
                </nav>

                <div className="absolute bottom-0 w-64 p-4 border-t">
                    <Button
                        variant="secondary"
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2"
                    >
                        <LogOut size={18} />
                        <span>Logout</span>
                    </Button>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="bg-white shadow-sm p-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-800">Dashboard</h2>
                        <div className="text-sm text-gray-600">
                            {/* TODO: Add user info here */}
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 overflow-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}

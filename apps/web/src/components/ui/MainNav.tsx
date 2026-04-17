'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTheme } from '@/components/providers/theme-provider';

export function MainNav() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const pathname = usePathname();
    const { theme, toggleTheme } = useTheme();

    const navItems = [
        { label: 'Inicio', href: '/' },
        { label: 'Precios', href: '/pricing' },
        { label: 'Plataforma', href: '/platform' },
    ];

    const isActive = (href: string) => pathname === href;

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-[#0f0f0f]/80 backdrop-blur-lg border-b border-gray-200 dark:border-[#27272a]">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center space-x-2 group">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#7C3AED] flex items-center justify-center shadow-accent transition-transform group-hover:scale-105">
                            <span className="text-white font-black text-xl">SO</span>
                        </div>
                        <span className="text-xl font-black bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] bg-clip-text text-transparent">
                            Sales Oracle
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`font-bold text-sm transition-colors relative group ${isActive(item.href)
                                    ? 'text-[#8B5CF6]'
                                    : 'text-gray-700 dark:text-gray-300 hover:text-[#8B5CF6] dark:hover:text-[#8B5CF6]'
                                    }`}
                            >
                                {item.label}
                                <span
                                    className={`absolute -bottom-1 left-0 h-0.5 bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] transition-all ${isActive(item.href) ? 'w-full' : 'w-0 group-hover:w-full'
                                        }`}
                                />
                            </Link>
                        ))}
                    </div>

                    {/* Right Side: Theme Toggle + Login Button - Desktop */}
                    <div className="hidden md:flex items-center space-x-4">
                        {/* Theme Toggle Button */}
                        <button
                            onClick={toggleTheme}
                            className="p-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-[#1a1a1a] transition-colors"
                            aria-label="Toggle theme"
                        >
                            {theme === 'light' ? (
                                <svg className="w-5 h-5 text-gray-700" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                    <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5 text-gray-300" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                    <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                            )}
                        </button>

                        <Link
                            href="/login"
                            className="px-6 py-2.5 bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] text-white font-bold rounded-xl shadow-accent hover:shadow-lg hover:scale-105 transition-all"
                        >
                            Iniciar Sesión
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-[#1a1a1a] transition-colors"
                        aria-label="Toggle menu"
                    >
                        <svg
                            className="w-6 h-6 text-gray-700 dark:text-gray-300"
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            {mobileMenuOpen ? (
                                <path d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-gray-200 dark:border-[#27272a] bg-white dark:bg-[#0f0f0f]">
                    <div className="px-4 py-4 space-y-3">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`block px-4 py-2 rounded-lg font-bold transition-colors ${isActive(item.href)
                                    ? 'bg-[#EDE9FE] text-[#8B5CF6] dark:bg-[#8B5CF6]/20'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#1a1a1a]'
                                    }`}
                            >
                                {item.label}
                            </Link>
                        ))}

                        {/* Theme Toggle in Mobile Menu */}
                        <button
                            onClick={toggleTheme}
                            className="w-full flex items-center justify-between px-4 py-2 rounded-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] transition-colors"
                        >
                            <span>{theme === 'light' ? 'Modo Oscuro' : 'Modo Claro'}</span>
                            {theme === 'light' ? (
                                <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                    <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                    <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                            )}
                        </button>

                        <Link
                            href="/login"
                            onClick={() => setMobileMenuOpen(false)}
                            className="block px-4 py-2.5 bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] text-white font-bold rounded-lg text-center shadow-accent"
                        >
                            Iniciar Sesión
                        </Link>
                    </div>
                </div>
            )}
        </nav>
    );
}

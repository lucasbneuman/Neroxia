"use client"

import { Moon, Sun } from "lucide-react"
import { useEffect, useState } from "react"

export function ThemeToggle() {
    const [theme, setTheme] = useState<"light" | "dark">("light")
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
        // Get theme from localStorage or default to light
        const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null
        const initialTheme = savedTheme || "light"
        setTheme(initialTheme)

        // Apply dark class to html element for Tailwind
        if (initialTheme === "dark") {
            document.documentElement.classList.add("dark")
        } else {
            document.documentElement.classList.remove("dark")
        }
    }, [])

    const toggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light"
        setTheme(newTheme)

        // Toggle dark class on html element for Tailwind
        if (newTheme === "dark") {
            document.documentElement.classList.add("dark")
        } else {
            document.documentElement.classList.remove("dark")
        }

        localStorage.setItem("theme", newTheme)
    }

    // Prevent hydration mismatch
    if (!mounted) {
        return (
            <button className="p-2 rounded-xl bg-gray-100 text-gray-400 w-10 h-10" disabled>
                <Sun size={20} />
            </button>
        )
    }

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-gradient-to-br from-purple-100 to-purple-50 hover:from-purple-200 hover:to-purple-100 text-purple-600 transition-smooth shadow-soft hover:shadow-medium dark:from-purple-900/30 dark:to-purple-800/30 dark:hover:from-purple-900/50 dark:hover:to-purple-800/50 dark:text-purple-400"
            aria-label={theme === "light" ? "Cambiar a modo oscuro" : "Cambiar a modo claro"}
            title={theme === "light" ? "Modo Oscuro" : "Modo Claro"}
        >
            {theme === "light" ? (
                <Moon size={20} className="transition-transform hover:rotate-12" />
            ) : (
                <Sun size={20} className="transition-transform hover:rotate-45" />
            )}
        </button>
    )
}

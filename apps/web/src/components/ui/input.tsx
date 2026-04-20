import * as React from "react"
import { cn } from "@/lib/utils"

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, ...props }, ref) => {
        return (
            <input
                type={type}
                className={cn(
                    "flex h-10 w-full rounded-xl border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-black dark:text-white px-4 py-2 text-sm font-bold transition-smooth placeholder:text-gray-400 dark:placeholder:text-gray-500 placeholder:font-normal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 focus-visible:border-purple-600 disabled:cursor-not-allowed disabled:opacity-50 shadow-soft",
                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Input.displayName = "Input"

export { Input }

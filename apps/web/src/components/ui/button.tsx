import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "primary" | "secondary" | "danger"
    size?: "default" | "sm" | "lg"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "default", size = "default", ...props }, ref) => {
        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center whitespace-nowrap rounded font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black disabled:pointer-events-none disabled:opacity-50",
                    {
                        // Variants
                        "bg-black text-white hover:bg-gray-800": variant === "default" || variant === "primary",
                        "bg-white text-black border border-black hover:bg-gray-50": variant === "secondary",
                        "bg-red-600 text-white hover:bg-red-700": variant === "danger",
                        // Sizes
                        "h-9 px-4 py-2 text-sm": size === "default",
                        "h-8 px-3 text-xs": size === "sm",
                        "h-11 px-8 text-base": size === "lg",
                    },
                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button }

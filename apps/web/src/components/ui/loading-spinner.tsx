import * as React from "react"
import { cn } from "@/lib/utils"

export interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
    size?: "sm" | "md" | "lg"
    variant?: "default" | "accent"
}

const LoadingSpinner = React.forwardRef<HTMLDivElement, LoadingSpinnerProps>(
    ({ className, size = "md", variant = "default", ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]",
                    {
                        "h-4 w-4 border-2": size === "sm",
                        "h-8 w-8 border-2": size === "md",
                        "h-12 w-12 border-3": size === "lg",
                        "text-gray-400": variant === "default",
                        "text-purple-600": variant === "accent",
                    },
                    className
                )}
                role="status"
                aria-label="Loading"
                {...props}
            >
                <span className="sr-only">Loading...</span>
            </div>
        )
    }
)
LoadingSpinner.displayName = "LoadingSpinner"

export { LoadingSpinner }

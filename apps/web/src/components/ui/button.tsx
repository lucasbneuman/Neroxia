import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "primary" | "secondary" | "danger" | "outline" | "ghost"
    size?: "default" | "sm" | "lg" | "icon"
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
        const buttonClasses = cn(
            "inline-flex items-center justify-center whitespace-nowrap font-bold transition-smooth focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
            {
                // Variants
                "bg-gradient-to-r from-purple-600 to-purple-500 text-white hover:from-purple-700 hover:to-purple-600 shadow-soft hover:shadow-medium rounded-2xl": variant === "default" || variant === "primary",
                "bg-white dark:bg-gray-800 text-black dark:text-white border-2 border-gray-300 dark:border-gray-600 hover:border-purple-600 dark:hover:border-purple-500 hover:text-purple-600 dark:hover:text-purple-400 shadow-soft hover:shadow-medium rounded-2xl": variant === "secondary" || variant === "outline",
                "bg-gradient-to-r from-red-600 to-red-500 text-white hover:from-red-700 hover:to-red-600 shadow-soft hover:shadow-medium rounded-2xl": variant === "danger",
                "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300": variant === "ghost",
                // Sizes
                "h-10 px-5 py-2 text-sm": size === "default",
                "h-8 px-4 text-xs": size === "sm",
                "h-12 px-8 text-base": size === "lg",
                "h-10 w-10 p-0": size === "icon",
            },
            className
        );

        if (asChild) {
            // When asChild is true, render the child element with button classes
            const child = React.Children.only(props.children as React.ReactElement);
            return React.cloneElement(child, {
                className: cn(buttonClasses, child.props.className),
                ref,
            });
        }

        return (
            <button
                className={buttonClasses}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button }

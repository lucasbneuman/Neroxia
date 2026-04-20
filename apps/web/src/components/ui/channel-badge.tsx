import { MessageCircle, Instagram, Facebook, Globe } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChannelBadgeProps {
  channel: "whatsapp" | "instagram" | "messenger" | "web"
  variant?: "default" | "outline"
  className?: string
}

export function ChannelBadge({ channel, variant = "default", className }: ChannelBadgeProps) {
  const config = {
    whatsapp: {
      icon: MessageCircle,
      label: "WhatsApp",
      defaultClass: "bg-green-500 hover:bg-green-600 text-white",
      outlineClass: "border-green-500 text-green-600 dark:text-green-400",
    },
    instagram: {
      icon: Instagram,
      label: "Instagram",
      defaultClass: "bg-pink-500 hover:bg-pink-600 text-white",
      outlineClass: "border-pink-500 text-pink-600 dark:text-pink-400",
    },
    messenger: {
      icon: Facebook,
      label: "Messenger",
      defaultClass: "bg-blue-500 hover:bg-blue-600 text-white",
      outlineClass: "border-blue-500 text-blue-600 dark:text-blue-400",
    },
    web: {
      icon: Globe,
      label: "Web",
      defaultClass: "bg-amber-500 hover:bg-amber-600 text-white",
      outlineClass: "border-amber-500 text-amber-600 dark:text-amber-400",
    },
  }

  const { icon: Icon, label, defaultClass, outlineClass } = config[channel]

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold transition-colors",
        variant === "default" ? defaultClass : `border ${outlineClass}`,
        className
      )}
    >
      <Icon className="w-3 h-3" />
      <span>{label}</span>
    </div>
  )
}

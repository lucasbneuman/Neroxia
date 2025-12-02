"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function CrmPage() {
    const router = useRouter()

    useEffect(() => {
        router.push("/dashboard/crm/dashboard")
    }, [router])

    return null
}

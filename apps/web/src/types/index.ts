// Type definitions for the application

export interface User {
    id: number
    phone: string
    name?: string
    email?: string
    conversation_mode: "AUTO" | "MANUAL" | "NEEDS_ATTENTION"
    total_messages: number
    last_message_at?: string
    sentiment?: string
    stage?: string
    conversation_summary?: string
}

export interface Message {
    id: number
    user_id: number
    message_text: string
    sender: "user" | "bot"
    created_at: string
    metadata?: Record<string, any>
}

export interface Conversation {
    user: User
    last_message: string
    unread: boolean
}

export interface Config {
    // Chatbot config
    system_prompt: string
    welcome_message: string
    payment_link: string
    response_delay_minutes: number
    text_audio_ratio: number
    use_emojis: boolean
    tts_voice: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer"
    multi_part_messages: boolean
    max_words_per_response: number

    // Product config
    product_name: string
    product_description: string
    product_features: string
    product_benefits: string
    product_price: string
    product_target_audience: string
}

export interface CollectedData {
    user_id: string
    name: string
    email: string
    phone: string
    last_contact: string
    intent: string
    sentiment: string
    stage: string
    needs: string
    requests_human: string
    notes: string
}

export interface RAGStats {
    total_chunks: number
}

export interface APIResponse<T = any> {
    success?: boolean  // Legacy field, some endpoints still use this
    status?: string    // New field: "success" | "error"
    data?: T
    error?: string
    message?: string
    configs?: any      // For config endpoints
}

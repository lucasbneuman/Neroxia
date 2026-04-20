// Type definitions for the application

export type JsonPrimitive = string | number | boolean | null
export type JsonValue = JsonPrimitive | JsonObject | JsonValue[]
export interface JsonObject {
    [key: string]: JsonValue
}

export interface User {
    id: number
    phone: string | null
    name?: string
    email?: string
    conversation_mode: "AUTO" | "MANUAL" | "NEEDS_ATTENTION"
    total_messages: number
    last_message_at?: string
    sentiment?: string
    stage?: string
    conversation_summary?: string

    // Multi-channel support
    channel: "whatsapp" | "instagram" | "messenger" | "web"
    channel_user_id?: string
    display_identifier?: string
    origin_host?: string

    // Analysis data
    intent_score?: number

    // WhatsApp/Twilio data
    whatsapp_profile_name?: string
    country_code?: string
    phone_formatted?: string
    first_contact_timestamp?: string
    media_count?: number
    location_shared?: boolean

    // Timestamps
    created_at?: string
    updated_at?: string
}

export interface Message {
    id: number
    user_id: number
    message_text: string
    sender: "user" | "bot"
    created_at: string
    timestamp?: string
    metadata?: JsonObject
    message_metadata?: {
        manual?: boolean
        agent?: string
        widget_id?: string
        session_id?: string
        origin?: string
        page_url?: string
        user_agent?: string
    }
    channel?: User["channel"]
}

export interface Conversation {
    user: User
    last_message: string
    unread: boolean
}

export interface WebWidgetConfig {
    enabled: boolean
    widget_id: string
    allowed_origins: string[]
    default_primary_color: string
    snippet: string
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

export interface APIResponse<T = unknown> {
    success?: boolean  // Legacy field, some endpoints still use this
    status?: string    // New field: "success" | "error"
    data?: T
    error?: string
    message?: string
    configs?: Partial<Config>
}

export interface Tag {
    id: number
    name: string
    color: string
    created_at: string
}

export interface Note {
    id: number
    user_id: number
    deal_id?: number
    content: string
    note_type: "note" | "call" | "email" | "meeting" | "task"
    created_by: string
    created_at: string
}

export interface Deal {
    id: number
    user_id: number
    title: string
    value: number
    currency: string
    stage: "new_lead" | "qualified" | "in_conversation" | "proposal_sent" | "won" | "lost"
    probability: number
    source: string
    manually_qualified: boolean
    expected_close_date?: string
    won_date?: string
    lost_date?: string
    lost_reason?: string
    created_at: string
    updated_at: string
    user?: User
    notes?: Note[]
}


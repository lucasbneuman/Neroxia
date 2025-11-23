import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error(
        'Missing Supabase environment variables. ' +
        'Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env file.'
    )
}

/**
 * Get Supabase client for client-side use only.
 * This prevents hydration mismatches by ensuring the client is only created on the client side.
 * 
 * @throws Error if called on server side
 */
export const getSupabaseClient = () => {
    if (typeof window === 'undefined') {
        throw new Error('Supabase client can only be created on the client side')
    }
    return createClientComponentClient()
}

// Helper function to get current session
export const getSession = async () => {
    const supabase = getSupabaseClient()
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) {
        console.error('Error getting session:', error)
        return null
    }
    return session
}

// Helper function to get current user
export const getCurrentUser = async () => {
    const supabase = getSupabaseClient()
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error) {
        console.error('Error getting user:', error)
        return null
    }
    return user
}

// Helper function to sign out
export const signOut = async () => {
    const supabase = getSupabaseClient()
    const { error } = await supabase.auth.signOut()
    if (error) {
        console.error('Error signing out:', error)
        throw error
    }
}


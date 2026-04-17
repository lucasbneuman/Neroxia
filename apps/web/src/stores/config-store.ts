import { create } from 'zustand'
import type { Config } from '@/types'

interface ConfigStore {
  config: Partial<Config>
  loading: boolean
  saving: boolean
  status: string
  setConfig: (config: Partial<Config>) => void
  updateConfig: (updates: Partial<Config>) => void
  setLoading: (loading: boolean) => void
  setSaving: (saving: boolean) => void
  setStatus: (status: string) => void
  reset: () => void
}

const initialConfig: Partial<Config> = {
  system_prompt: '',
  welcome_message: '',
  payment_link: '',
  response_delay_minutes: 0.5,
  text_audio_ratio: 0,
  use_emojis: true,
  tts_voice: 'nova',
  multi_part_messages: false,
  max_words_per_response: 100,
  product_name: '',
  product_description: '',
  product_features: '',
  product_benefits: '',
  product_price: '',
  product_target_audience: '',
}

export const useConfigStore = create<ConfigStore>((set) => ({
  config: initialConfig,
  loading: true,
  saving: false,
  status: '',
  setConfig: (config) => set({ config }),
  updateConfig: (updates) => set((state) => ({
    config: { ...state.config, ...updates }
  })),
  setLoading: (loading) => set({ loading }),
  setSaving: (saving) => set({ saving }),
  setStatus: (status) => set({ status }),
  reset: () => set({
    config: initialConfig,
    loading: true,
    saving: false,
    status: ''
  }),
}))

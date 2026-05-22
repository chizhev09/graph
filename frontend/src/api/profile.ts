import { apiClient } from './client'

export type UserProfile = {
  id: number
  telegram_id: number
  username: string | null
  first_name: string | null
  is_premium: boolean
  daily_notifications_used: number
  notifications_remaining: number | null
  max_searches: number
  active_searches: number
}

export async function getProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>('/profile')
  return data
}

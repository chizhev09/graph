import { apiClient } from './client'

export type SubscriptionStatus = {
  is_premium: boolean
  daily_notifications_used: number
  daily_notifications_limit: number | null
  notifications_remaining: number | null
  max_searches: number
  active_searches: number
}

export async function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  const { data } = await apiClient.get<SubscriptionStatus>('/subscriptions/status')
  return data
}

export async function checkPremium(): Promise<{ is_premium: boolean; message: string }> {
  const { data } = await apiClient.post('/subscriptions/check')
  return data
}

import { apiClient, setTokens } from './client'

export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function authWithTelegram(initData: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/telegram', {
    init_data: initData,
  })
  setTokens(data.access_token, data.refresh_token)
  return data
}

/** Вход для локальной разработки в браузере (без Telegram). */
export async function authDev(): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/dev')
  setTokens(data.access_token, data.refresh_token)
  return data
}

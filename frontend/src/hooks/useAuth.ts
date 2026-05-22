import { useEffect, useState } from 'react'
import { authDev, authWithTelegram } from '../api/auth'
import { getProfile, type UserProfile } from '../api/profile'

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string
        ready: () => void
        expand: () => void
      }
    }
  }
}

export function useAuth() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function init() {
      try {
        const tg = window.Telegram?.WebApp
        if (tg?.initData) {
          tg.ready()
          tg.expand()
          await authWithTelegram(tg.initData)
        } else if (import.meta.env.DEV) {
          const hasToken = localStorage.getItem('graph_access_token')
          if (!hasToken) {
            await authDev()
          }
        }
        const p = await getProfile()
        if (!cancelled) setProfile(p)
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Auth failed')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    init()
    return () => {
      cancelled = true
    }
  }, [])

  return { profile, loading, error }
}

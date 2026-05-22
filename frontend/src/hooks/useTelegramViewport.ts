import { useEffect } from 'react'

const TG_HEADER_FALLBACK_PX = 52

function applySafeAreaInsets() {
  const tg = window.Telegram?.WebApp
  const root = document.documentElement

  if (!tg) {
    root.style.setProperty('--tg-safe-top', '0px')
    root.style.setProperty('--tg-safe-bottom', '0px')
    root.style.setProperty('--tg-safe-left', '0px')
    root.style.setProperty('--tg-safe-right', '0px')
    return
  }

  const content = tg.contentSafeAreaInset
  const safe = tg.safeAreaInset

  let top = content?.top ?? safe?.top ?? 0
  if (top < TG_HEADER_FALLBACK_PX) {
    top = TG_HEADER_FALLBACK_PX
  }

  root.style.setProperty('--tg-safe-top', `${top}px`)
  root.style.setProperty('--tg-safe-bottom', `${content?.bottom ?? safe?.bottom ?? 0}px`)
  root.style.setProperty('--tg-safe-left', `${content?.left ?? safe?.left ?? 0}px`)
  root.style.setProperty('--tg-safe-right', `${content?.right ?? safe?.right ?? 0}px`)
}

export function useTelegramViewport() {
  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (!tg) return

    tg.ready()
    tg.expand()
    tg.setBackgroundColor('#000000')
    tg.setHeaderColor('#000000')

    applySafeAreaInsets()

    const events = ['viewportChanged', 'safeAreaChanged', 'contentSafeAreaChanged'] as const
    for (const event of events) {
      tg.onEvent(event, applySafeAreaInsets)
    }

    return () => {
      for (const event of events) {
        tg.offEvent(event, applySafeAreaInsets)
      }
    }
  }, [])
}

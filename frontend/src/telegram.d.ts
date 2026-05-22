interface SafeAreaInset {
  top: number
  bottom: number
  left: number
  right: number
}

interface TelegramWebApp {
  initData: string
  ready: () => void
  expand: () => void
  close: () => void
  platform: string
  isExpanded?: boolean
  safeAreaInset?: SafeAreaInset
  contentSafeAreaInset?: SafeAreaInset
  setBackgroundColor: (color: string) => void
  setHeaderColor: (color: string) => void
  onEvent: (event: string, handler: () => void) => void
  offEvent: (event: string, handler: () => void) => void
}

interface Window {
  Telegram?: {
    WebApp: TelegramWebApp
  }
}

export type SourceId = 'avito' | 'youla' | 'telegram' | 'vk'

export type Source = {
  id: SourceId
  label: string
}

export const SOURCES: Source[] = [
  { id: 'avito', label: 'Авито' },
  { id: 'youla', label: 'Юла' },
  { id: 'telegram', label: 'Telegram' },
  { id: 'vk', label: 'ВК' },
]

export const DEFAULT_SOURCE_IDS: SourceId[] = SOURCES.map((s) => s.id)

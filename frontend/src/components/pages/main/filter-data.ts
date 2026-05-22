export type { City } from './cities-data'
export { CITIES } from './cities-data'
export type { Source, SourceId } from './sources-data'
export { SOURCES, DEFAULT_SOURCE_IDS } from './sources-data'

export type CategoryId =
  | 'phones'
  | 'laptops'
  | 'gpus'
  | 'consoles'
  | 'watches'
  | 'cameras'
  | 'audio'
  | 'pc-parts'

export type Category = {
  id: CategoryId
  emoji: string
  label: string
}

export const CATEGORIES: Category[] = [
  { id: 'phones', emoji: '📱', label: 'Телефоны' },
  { id: 'laptops', emoji: '💻', label: 'Ноутбуки' },
  { id: 'gpus', emoji: '🖥', label: 'Видеокарты' },
  { id: 'consoles', emoji: '🎮', label: 'Консоли' },
  { id: 'watches', emoji: '⌚', label: 'Смарт-часы' },
  { id: 'cameras', emoji: '📷', label: 'Камеры' },
  { id: 'audio', emoji: '🎧', label: 'Аудио' },
  { id: 'pc-parts', emoji: '⌨️', label: 'ПК-комплектующие' },
]

export type ExclusionId =
  | 'resellers'
  | 'shops'
  | 'companies'
  | 'wholesale'
  | 'dealers'
  | 'delivery-only'

export type Exclusion = {
  id: ExclusionId
  emoji: string
  label: string
}

export const EXCLUSIONS: Exclusion[] = [
  { id: 'resellers', emoji: '🔄', label: 'Перекупы' },
  { id: 'shops', emoji: '🏪', label: 'Магазины' },
  { id: 'companies', emoji: '🏢', label: 'Компании' },
  { id: 'wholesale', emoji: '📦', label: 'Оптом' },
  { id: 'dealers', emoji: '🛒', label: 'Дилеры' },
  { id: 'delivery-only', emoji: '🚚', label: 'Только доставка' },
]

export const BRANDS_BY_CATEGORY: Record<CategoryId, string[]> = {
  phones: ['Apple', 'Samsung', 'Xiaomi', 'Google', 'OnePlus'],
  laptops: ['Apple', 'ASUS', 'Lenovo', 'MSI', 'Dell'],
  gpus: ['NVIDIA', 'AMD', 'ASUS', 'Gigabyte', 'MSI'],
  consoles: ['PlayStation', 'Xbox', 'Nintendo'],
  watches: ['Apple', 'Samsung', 'Garmin'],
  cameras: ['Sony', 'Canon', 'Fujifilm', 'Nikon'],
  audio: ['AirPods', 'Sony', 'Marshall', 'JBL'],
  'pc-parts': ['Intel', 'AMD', 'Corsair', 'ASUS', 'NZXT'],
}

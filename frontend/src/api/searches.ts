import { apiClient } from './client'

export type SearchPayload = {
  city: string
  category?: string | null
  brands: string[]
  exclusions: string[]
  source_types?: string[]
  active?: boolean
}

export type SearchResponse = SearchPayload & {
  id: number
  user_id: number
  created_at: string
  updated_at: string
}

export async function createSearch(payload: SearchPayload): Promise<SearchResponse> {
  const { data } = await apiClient.post<SearchResponse>('/searches', payload)
  return data
}

export async function listSearches(): Promise<SearchResponse[]> {
  const { data } = await apiClient.get<SearchResponse[]>('/searches')
  return data
}

export async function deactivateAllSearches(): Promise<void> {
  const searches = await listSearches()
  await Promise.all(
    searches.map((s) =>
      apiClient.patch(`/searches/${s.id}`, { active: false }),
    ),
  )
}

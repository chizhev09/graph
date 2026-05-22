import { useEffect, useId, useMemo, useRef, useState } from 'react'
import type { City } from './filter-data'
import './city-select.css'

type CitySelectProps = {
  cities: readonly City[]
  value: string
  onChange: (id: string) => void
}

export function CitySelect({ cities, value, onChange }: CitySelectProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const rootRef = useRef<HTMLDivElement>(null)
  const listId = useId()

  const selected = cities.find((c) => c.id === value)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return cities
    return cities.filter((c) => c.label.toLowerCase().includes(q))
  }, [cities, query])

  useEffect(() => {
    if (!open) return

    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false)
        setQuery('')
      }
    }

    document.addEventListener('mousedown', onPointerDown)
    return () => document.removeEventListener('mousedown', onPointerDown)
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
        setQuery('')
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open])

  const pick = (id: string) => {
    onChange(id)
    setOpen(false)
    setQuery('')
  }

  return (
    <div className={`city-select${open ? ' city-select--open' : ''}`} ref={rootRef}>
      <button
        type="button"
        className="city-select__trigger"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-controls={listId}
        onClick={() => setOpen((prev) => !prev)}
      >
        <span className="city-select__value">{selected?.label ?? 'Выберите город'}</span>
        <span className="city-select__chevron" aria-hidden />
      </button>

      {open && (
        <div className="city-select__panel">
          <div className="city-select__search-wrap">
            <input
              type="search"
              className="city-select__search"
              placeholder="Поиск города..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoComplete="off"
              aria-label="Поиск города"
            />
          </div>
          <ul id={listId} className="city-select__list" role="listbox" aria-label="Город">
            {filtered.length === 0 ? (
              <li className="city-select__empty">Ничего не найдено</li>
            ) : (
              filtered.map((city) => {
                const isSelected = city.id === value
                return (
                  <li key={city.id} role="presentation">
                    <button
                      type="button"
                      role="option"
                      aria-selected={isSelected}
                      className={`city-select__option${isSelected ? ' city-select__option--active' : ''}`}
                      onClick={() => pick(city.id)}
                    >
                      {city.label}
                      {isSelected && <span className="city-select__check" aria-hidden />}
                    </button>
                  </li>
                )
              })
            )}
          </ul>
        </div>
      )}
    </div>
  )
}

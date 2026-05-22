import { useEffect, useMemo, useState } from 'react'
import { createSearch, deactivateAllSearches } from '../../../api/searches'
import { getSubscriptionStatus, type SubscriptionStatus } from '../../../api/subscriptions'
import { useAuth } from '../../../hooks/useAuth'
import {
  BRANDS_BY_CATEGORY,
  CATEGORIES,
  CITIES,
  DEFAULT_SOURCE_IDS,
  EXCLUSIONS,
  SOURCES,
  type CategoryId,
  type ExclusionId,
  type SourceId,
} from './filter-data'
import { Divider } from './divider'
import './main.css'

const HERO_IMAGE = '/hiro_image.webp'
const HERO_IMAGE_SUCCESS = '/hiro_image_sucsess.webp'
const DEFAULT_CITY = 'moscow'

const MENU_ITEMS = [
  { id: 'home', label: 'Главная' },
  { id: 'filters', label: 'Мои фильтры' },
  { id: 'settings', label: 'Настройки' },
  { id: 'about', label: 'О приложении' },
] as const

type SelectedBrands = Partial<Record<CategoryId, Set<string>>>

function isCategoryFullySelected(
  selected: SelectedBrands,
  categoryId: CategoryId,
): boolean {
  const brands = selected[categoryId]
  if (!brands?.size) return false
  return BRANDS_BY_CATEGORY[categoryId].every((name) => brands.has(name))
}

function countSelected(selected: SelectedBrands): number {
  return Object.values(selected).reduce((sum, brands) => sum + (brands?.size ?? 0), 0)
}

export function Main() {
  const { profile } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const [menuView, setMenuView] = useState<'nav' | 'settings'>('nav')
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [selectedCity, setSelectedCity] = useState(DEFAULT_CITY)
  const [selectedSources, setSelectedSources] = useState<Set<SourceId>>(
    () => new Set(DEFAULT_SOURCE_IDS),
  )
  const [selected, setSelected] = useState<SelectedBrands>({})
  const [exclusions, setExclusions] = useState<Set<ExclusionId>>(new Set())
  const [isTracking, setIsTracking] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const activeFiltersCount = useMemo(
    () =>
      countSelected(selected) +
      exclusions.size +
      selectedSources.size +
      (selectedCity ? 1 : 0),
    [selected, exclusions, selectedSources, selectedCity],
  )

  const selectCategory = (id: CategoryId) => {
    setSelected((prev) => {
      const next: SelectedBrands = { ...prev }
      if (isCategoryFullySelected(prev, id)) {
        delete next[id]
      } else {
        next[id] = new Set(BRANDS_BY_CATEGORY[id])
      }
      return next
    })
  }

  const toggleSource = (id: SourceId) => {
    setSelectedSources((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        if (next.size > 1) next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const toggleExclusion = (id: ExclusionId) => {
    setExclusions((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const selectBrand = (id: CategoryId, name: string) => {
    setSelected((prev) => {
      const next: SelectedBrands = { ...prev }
      const brands = new Set(prev[id] ?? [])

      if (brands.has(name)) brands.delete(name)
      else brands.add(name)

      if (brands.size === 0) delete next[id]
      else next[id] = brands

      return next
    })
  }

  const handleTracking = async () => {
    if (isTracking) {
      setSubmitting(true)
      try {
        await deactivateAllSearches()
        setIsTracking(false)
      } catch {
        /* keep tracking state on error */
      } finally {
        setSubmitting(false)
      }
      return
    }

    const hasFilters = countSelected(selected) > 0
    if (!hasFilters || selectedSources.size === 0) return

    const sourceTypes = Array.from(selectedSources)

    setSubmitting(true)
    try {
      const tasks = Object.entries(selected).map(([categoryId, brands]) =>
        createSearch({
          city: selectedCity,
          category: categoryId,
          brands: Array.from(brands ?? []),
          exclusions: Array.from(exclusions),
          source_types: sourceTypes,
          active: true,
        }),
      )
      await Promise.all(tasks)
      setIsTracking(true)
    } catch {
      /* auth or limit error */
    } finally {
      setSubmitting(false)
    }
  }

  const openMenu = (view: 'nav' | 'settings' = 'nav') => {
    setMenuView(view)
    setMenuOpen(true)
  }

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [menuOpen])

  useEffect(() => {
    if (!menuOpen) return

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false)
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  useEffect(() => {
    if (menuView !== 'settings' || !menuOpen) return
    getSubscriptionStatus()
      .then(setSubscription)
      .catch(() => setSubscription(null))
  }, [menuView, menuOpen])

  return (
    <div className="main">
      <header className="main__header">
        <h1 className="main__title">Graph</h1>
        <button
          type="button"
          className="main__menu-btn"
          aria-label="Открыть меню"
          aria-expanded={menuOpen}
          onClick={() => openMenu('nav')}
        >
          <span className="main__menu-line" />
          <span className="main__menu-line" />
        </button>
      </header>

      {menuOpen && (
        <div
          className="main__modal"
          role="dialog"
          aria-modal="true"
          aria-label="Меню"
        >
          <div className="main__modal-top">
            <span className="main__modal-title">
              {menuView === 'settings' ? 'Настройки' : 'Меню'}
            </span>
            <button
              type="button"
              className="main__modal-close"
              aria-label="Закрыть меню"
              onClick={() => setMenuOpen(false)}
            >
              <span className="main__menu-line main__menu-line--close" />
              <span className="main__menu-line main__menu-line--close" />
            </button>
          </div>
          {menuView === 'settings' ? (
            <div className="main__modal-settings">
              <p className="main__modal-settings-line">
                Premium: {subscription?.is_premium || profile?.is_premium ? 'активен' : 'нет'}
              </p>
              <p className="main__modal-settings-line">
                Уведомлений сегодня: {subscription?.daily_notifications_used ?? profile?.daily_notifications_used ?? 0}
                {subscription && !subscription.is_premium && subscription.daily_notifications_limit != null
                  ? ` / ${subscription.daily_notifications_limit}`
                  : ''}
              </p>
              {subscription && !subscription.is_premium && (
                <p className="main__modal-settings-line">
                  Осталось: {subscription.notifications_remaining ?? 0}
                </p>
              )}
              <p className="main__modal-settings-line">
                Активных подписок: {subscription?.active_searches ?? profile?.active_searches ?? 0}
              </p>
            </div>
          ) : (
            <nav className="main__modal-nav">
              <ul className="main__modal-list">
                {MENU_ITEMS.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      className="main__modal-link"
                      onClick={() => {
                        if (item.id === 'settings') {
                          setMenuView('settings')
                        } else {
                          setMenuOpen(false)
                        }
                      }}
                    >
                      {item.label}
                    </button>
                  </li>
                ))}
              </ul>
            </nav>
          )}
        </div>
      )}

      <div className="main__hero-screen">
      <section className="main__hero">
        <h2 className="main__headline">
          Ловите объявления <span>раньше других</span>
        </h2>
        <p className="main__subtitle">
          Настройте фильтры и нажмите кнопку — пришлём новые объявления в Telegram за
          секунды.
        </p>
      </section>

      <div className="main__hero-image-wrap">
        <img
          className="main__hero-image"
          src={isTracking ? HERO_IMAGE_SUCCESS : HERO_IMAGE}
          alt={isTracking ? 'Отслеживание запущено' : 'Graph — мониторинг объявлений'}
          width={320}
          height={320}
        />
      </div>

      <div className="main__submit-wrap">
        <button
          type="button"
          className="main__submit"
          disabled={submitting}
          onClick={handleTracking}
        >
          {isTracking ? 'Отслеживание активно' : 'Начать отслеживание'}
        </button>
      </div>
      </div>

      <Divider variant="double" />

      <section className="main__picker" aria-labelledby="filters-heading">
        <div className="main__picker-head">
          <h3 id="filters-heading" className="main__picker-title">
            Мои фильтры
          </h3>
          <span className="main__count">{activeFiltersCount}</span>
        </div>

        <div className="main__filter-groups">
          <div className="main__city-section" aria-labelledby="city-heading">
            <h4 id="city-heading" className="main__exclusions-title">
              Город
            </h4>
            <div className="main__chips main__chips--scroll" role="group" aria-label="Город">
              {CITIES.map((city) => {
                const isActive = selectedCity === city.id
                return (
                  <button
                    key={city.id}
                    type="button"
                    className={`main__chip main__chip--brand${isActive ? ' main__chip--active' : ''}`}
                    aria-pressed={isActive}
                    onClick={() => setSelectedCity(city.id)}
                  >
                    <span className="main__chip-label">{city.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <Divider variant="single" />

          <div className="main__city-section" aria-labelledby="sources-heading">
            <h4 id="sources-heading" className="main__exclusions-title">
              Источники
            </h4>
            <div className="main__chips" role="group" aria-label="Источники">
              {SOURCES.map((source) => {
                const isActive = selectedSources.has(source.id)
                return (
                  <button
                    key={source.id}
                    type="button"
                    className={`main__chip main__chip--brand${isActive ? ' main__chip--active' : ''}`}
                    aria-pressed={isActive}
                    onClick={() => toggleSource(source.id)}
                  >
                    <span className="main__chip-label">{source.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <Divider variant="single" />

          {CATEGORIES.map((category, index) => {
            const isCategoryActive = isCategoryFullySelected(selected, category.id)
            return (
              <div key={category.id}>
                <div className="main__filter-group">
                <button
                  type="button"
                  className={`main__chip main__chip--category${isCategoryActive ? ' main__chip--active' : ''}`}
                  aria-pressed={isCategoryActive}
                  onClick={() => selectCategory(category.id)}
                >
                  <span className="main__chip-emoji" aria-hidden>
                    {category.emoji}
                  </span>
                  <span className="main__chip-label">{category.label}</span>
                </button>

                <div
                  className="main__chips"
                  role="group"
                  aria-label={`Бренды: ${category.label}`}
                >
                  {BRANDS_BY_CATEGORY[category.id].map((name) => {
                    const isBrandActive = selected[category.id]?.has(name) ?? false
                    return (
                      <button
                        key={name}
                        type="button"
                        className={`main__chip main__chip--brand${isBrandActive ? ' main__chip--active' : ''}`}
                        aria-pressed={isBrandActive}
                        onClick={() => selectBrand(category.id, name)}
                      >
                        <span className="main__chip-label">{name}</span>
                      </button>
                    )
                  })}
                </div>
                </div>

                {index < CATEGORIES.length - 1 && <Divider variant="single" />}
              </div>
            )
          })}

          <Divider variant="single" />

          <div className="main__exclusions" aria-labelledby="exclusions-heading">
            <h4 id="exclusions-heading" className="main__exclusions-title">
              Исключения
            </h4>
            <p className="main__exclusions-hint">
              Не присылать объявления от перекупов, магазинов и похожих продавцов
            </p>
            <div
              className="main__chips"
              role="group"
              aria-label="Исключения"
            >
              {EXCLUSIONS.map((item) => {
                const isActive = exclusions.has(item.id)
                return (
                  <button
                    key={item.id}
                    type="button"
                    className={`main__chip main__chip--exclusion${isActive ? ' main__chip--active' : ''}`}
                    aria-pressed={isActive}
                    onClick={() => toggleExclusion(item.id)}
                  >
                    <span className="main__chip-emoji" aria-hidden>
                      {item.emoji}
                    </span>
                    <span className="main__chip-label">{item.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <Divider variant="double" />
        </div>
      </section>
    </div>
  )
}

export default Main

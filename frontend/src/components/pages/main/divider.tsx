import './divider.css'

const ZIGZAG_A =
  'M0 16 L20 8 L40 16 L60 8 L80 16 L100 8 L120 16 L140 8 L160 16 L180 8 L200 16 L220 8 L240 16 L260 8 L280 16 L300 8 L320 16 L340 8 L360 16 L380 8 L400 16'

const ZIGZAG_B =
  'M0 32 L20 24 L40 32 L60 24 L80 32 L100 24 L120 32 L140 24 L160 32 L180 24 L200 32 L220 24 L240 32 L260 24 L280 32 L300 24 L320 32 L340 24 L360 32 L380 24 L400 32'

const ZIGZAG_SINGLE =
  'M0 12 L20 4 L40 12 L60 4 L80 12 L100 4 L120 12 L140 4 L160 12 L180 4 L200 12 L220 4 L240 12 L260 4 L280 12 L300 4 L320 12 L340 4 L360 12 L380 4 L400 12'

type DividerProps = {
  variant?: 'single' | 'double'
}

export function Divider({ variant = 'double' }: DividerProps) {
  const isDouble = variant === 'double'

  return (
    <div
      className={`main-divider main-divider--${variant}`}
      aria-hidden
    >
      <svg
        className="main-divider__svg"
        viewBox={isDouble ? '0 0 400 44' : '0 0 400 24'}
        preserveAspectRatio="none"
      >
        <path
          className="main-divider__line"
          d={isDouble ? ZIGZAG_A : ZIGZAG_SINGLE}
        />
        {isDouble && (
          <path
            className="main-divider__line main-divider__line--2"
            d={ZIGZAG_B}
          />
        )}
      </svg>
    </div>
  )
}

export default Divider

import { signalColor, signalLabel, formatTimestamp } from '../lib/format'

export default function Header({ signals, lastUpdated, isOffline }) {
  const tickers = ['SPY', 'QQQ', 'IWM', 'RSP']

  return (
    <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-stone-200">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold tracking-tight text-stone-900">
          Fluxus Capital
        </h1>
        {isOffline && (
          <span className="px-1.5 py-0.5 text-[9px] font-medium uppercase tracking-wider bg-stone-200 text-stone-600 rounded">
            Offline
          </span>
        )}
      </div>

      <div className="hidden sm:flex items-center gap-3">
        {tickers.map((ticker) => {
          const s = signals?.[ticker]
          if (!s) return null
          return (
            <div key={ticker} className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${signalColor(s.color)}`} />
              <span className="font-mono text-xs font-medium text-stone-800">
                {ticker}
              </span>
              <span className="text-[10px] text-stone-400 uppercase tracking-wide">
                {signalLabel(s.signal)}
              </span>
            </div>
          )
        })}
      </div>

      <div className="text-[10px] text-stone-400 font-mono">
        {formatTimestamp(lastUpdated)}
      </div>
    </header>
  )
}

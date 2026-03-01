import { signalColor, signalLabel } from '../../lib/format'

const TICKERS = ['SPY', 'QQQ', 'IWM', 'RSP']

export default function SignalLights({ signals }) {
  if (!signals) return null

  return (
    <div>
      <h3 className="text-[10px] font-medium uppercase tracking-wide text-stone-500 mb-2">
        Signal
      </h3>
      <div className="flex flex-col gap-1.5">
        {TICKERS.map((ticker) => {
          const s = signals[ticker]
          if (!s) return null
          return (
            <div key={ticker} className="flex items-center gap-2">
              <span
                className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${signalColor(s.color)}`}
              />
              <span className="font-mono text-sm text-stone-800">
                {ticker}
              </span>
              <span className="text-xs text-stone-500">
                {signalLabel(s.signal)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

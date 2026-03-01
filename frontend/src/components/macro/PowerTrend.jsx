const CHECKS = [
  { key: '3d_gt_20sma', label: 'Close > 20 SMA (3d)' },
  { key: '3d_gt_50sma', label: 'Close > 50 SMA (3d)' },
  { key: '3d_gt_200sma', label: 'Close > 200 SMA (3d)' },
  { key: '20sma_gt_50sma', label: '20 SMA > 50 SMA' },
  { key: '50sma_gt_200sma', label: '50 SMA > 200 SMA' },
]

export default function PowerTrend({ signals }) {
  const pt = signals?.QQQ?.power_trend
  if (!pt) return null

  return (
    <div>
      <h3 className="text-[10px] font-medium uppercase tracking-wide text-stone-500 mb-2">
        QQQ Power Trend
      </h3>
      <div className="flex flex-col gap-1.5">
        {CHECKS.map((check) => {
          const passed = pt[check.key]
          return (
            <div
              key={check.key}
              className="flex items-center justify-between"
            >
              <span className="text-xs text-stone-600">
                {check.label}
              </span>
              <span
                className={`font-mono text-xs ${
                  passed ? 'text-green-600' : 'text-red-500'
                }`}
              >
                {passed ? 'Yes' : 'No'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

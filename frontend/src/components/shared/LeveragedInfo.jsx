import { useState } from 'react'

export default function LeveragedInfo({ longEtfs, shortEtfs }) {
  const [show, setShow] = useState(false)

  const hasLong = longEtfs && longEtfs.length > 0
  const hasShort = shortEtfs && shortEtfs.length > 0

  if (!hasLong && !hasShort) return null

  return (
    <span
      className="relative inline-block"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <span className="cursor-default text-[9px] font-mono text-stone-400 leading-none">
        {hasLong && <span>L:{longEtfs.join(',')}</span>}
        {hasLong && hasShort && <span> </span>}
        {hasShort && <span>S:{shortEtfs.join(',')}</span>}
      </span>

      {show && (
        <span className="absolute bottom-full left-0 mb-1 z-10 whitespace-nowrap bg-white border border-stone-200 rounded px-2 py-1 text-[10px] font-mono text-stone-600">
          {hasLong && <span className="block">Long: {longEtfs.join(', ')}</span>}
          {hasShort && <span className="block">Short: {shortEtfs.join(', ')}</span>}
        </span>
      )}
    </span>
  )
}

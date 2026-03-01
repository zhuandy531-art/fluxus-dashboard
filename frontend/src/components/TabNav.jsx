const TABS = [
  { id: 'macro', label: 'Macro' },
  { id: 'equities', label: 'Equities' },
  { id: 'screeners', label: 'Scan' },
]

export default function TabNav({ activeTab, onTabChange }) {
  return (
    <nav className="flex border-b border-stone-200 bg-white sm:hidden">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`flex-1 py-2.5 text-xs font-medium uppercase tracking-wide transition-colors
            ${activeTab === tab.id
              ? 'text-stone-900 border-b-2 border-stone-900'
              : 'text-stone-400 hover:text-stone-600'
            }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}

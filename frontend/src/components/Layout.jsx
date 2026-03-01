import { useState } from 'react'
import Header from './Header'
import TabNav from './TabNav'
import MacroSection from './macro/MacroSection'
import EquitiesSection from './equities/EquitiesSection'
import ScreenersSection from './screeners/ScreenersSection'
import Footer from './Footer'

export default function Layout({ data, lastUpdated, isOffline }) {
  const [activeTab, setActiveTab] = useState('macro')

  return (
    <div className="min-h-screen bg-[#fafaf9]">
      <Header
        signals={data.signals}
        lastUpdated={lastUpdated}
        isOffline={isOffline}
      />
      <TabNav activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="max-w-[1800px] mx-auto px-2 py-3">
        {/* Desktop: 3-column grid */}
        <div className="hidden sm:grid sm:grid-cols-3 gap-3">
          <MacroSection data={data} />
          <EquitiesSection data={data} />
          <ScreenersSection data={data} />
        </div>

        {/* Mobile: tab content */}
        <div className="sm:hidden">
          {activeTab === 'macro' && <MacroSection data={data} />}
          {activeTab === 'equities' && <EquitiesSection data={data} />}
          {activeTab === 'screeners' && <ScreenersSection data={data} />}
        </div>
      </main>

      <Footer lastUpdated={lastUpdated} isOffline={isOffline} />
    </div>
  )
}

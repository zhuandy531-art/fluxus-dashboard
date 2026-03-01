import StockbeeRatio from './StockbeeRatio'
import Momentum97 from './Momentum97'
import Ema21Watch from './Ema21Watch'
import HealthyCharts from './HealthyCharts'
import Gainers4Pct from './Gainers4Pct'
import VolUpGainers from './VolUpGainers'
import VcpResults from './VcpResults'
import EpisodicPivot from './EpisodicPivot'
import ScreenerSection from './ScreenerSection'

export default function ScreenersSection({ data }) {
  if (!data) return null

  return (
    <div className="flex flex-col gap-2">
      <StockbeeRatio data={data.stockbee_ratio} />

      {data.momentum_97 && (
        <ScreenerSection title="Momentum 97+" count={data.momentum_97.count}>
          <Momentum97 data={data.momentum_97} />
        </ScreenerSection>
      )}

      {data.ema21_watch && (
        <ScreenerSection title="EMA 21 Watch" count={data.ema21_watch.count}>
          <Ema21Watch data={data.ema21_watch} />
        </ScreenerSection>
      )}

      {data.healthy_charts && (
        <ScreenerSection title="Healthy Charts" count={data.healthy_charts.count}>
          <HealthyCharts data={data.healthy_charts} />
        </ScreenerSection>
      )}

      {data.gainers_4pct && (
        <ScreenerSection title="Gainers 4%+" count={data.gainers_4pct.count}>
          <Gainers4Pct data={data.gainers_4pct} />
        </ScreenerSection>
      )}

      {data.vol_up_gainers && (
        <ScreenerSection title="Vol Up Gainers" count={data.vol_up_gainers.count}>
          <VolUpGainers data={data.vol_up_gainers} />
        </ScreenerSection>
      )}

      {data.vcp && (
        <ScreenerSection title="VCP" count={data.vcp.count}>
          <VcpResults data={data.vcp} />
        </ScreenerSection>
      )}

      {data.episodic_pivot && (
        <ScreenerSection title="Episodic Pivot" count={data.episodic_pivot.count}>
          <EpisodicPivot data={data.episodic_pivot} />
        </ScreenerSection>
      )}
    </div>
  )
}

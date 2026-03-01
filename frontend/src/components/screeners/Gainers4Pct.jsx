import TickerGrid from './TickerGrid'

export default function Gainers4Pct({ data }) {
  if (!data?.tickers) return null

  return <TickerGrid tickers={data.tickers} />
}

import TickerGrid from './TickerGrid'

export default function VolUpGainers({ data }) {
  if (!data?.tickers) return null

  return <TickerGrid tickers={data.tickers} />
}

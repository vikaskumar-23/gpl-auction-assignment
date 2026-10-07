import { useState } from 'react'
import { api } from '../lib/api'
import { money } from '../lib/format'
import { Button, ErrorText } from './ui'

const RAISES = [5, 10, 25, 50]

// no min/max on the input on purpose: the server's error message explains the rule
export default function BidBox({ team, auction }) {
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { player, bids } = auction
  const top = bids[0]
  const toBeat = player ? Math.max(player.base_price, top?.amount ?? 0) : 0

  const waiting = !player
    ? 'Waiting for the auctioneer to put a player up.'
    : top?.team_id === team.id
      ? 'You hold the highest bid. Wait for another team to bid.'
      : null

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.bid(team.id, Number(amount))
      setAmount('')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-6 rounded-2xl bg-paper p-4 sm:p-5">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <h3 className="font-display text-base font-semibold">Your bid</h3>
        <span className="text-sm text-slate">
          {team.name} have <strong className="font-semibold text-ink">{money(team.remaining_budget)}</strong> left
        </span>
      </div>
      {waiting ? (
        <p className="text-slate">{waiting}</p>
      ) : (
        <form onSubmit={submit}>
          <label htmlFor="bid-amount" className="block text-sm text-slate">
            Amount in ₹ lakh, more than {toBeat} ({money(toBeat)})
          </label>
          <div className="mt-2 flex gap-2">
            <div className="relative min-w-0 flex-1">
              <input
                id="bid-amount"
                type="number"
                inputMode="numeric"
                step="1"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder={String(toBeat + 5)}
                className="h-12 w-full min-w-0 appearance-none rounded-xl border border-line bg-card pr-14 pl-3 text-base font-semibold tabular-nums [-moz-appearance:textfield] placeholder:font-normal placeholder:text-slate/70 focus:border-cobalt focus:ring-4 focus:ring-cobalt/15 focus:outline-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
              />
              <span aria-hidden className="pointer-events-none absolute inset-y-0 right-3 grid place-items-center text-sm text-slate">
                lakh
              </span>
            </div>
            <Button type="submit" disabled={busy || !amount} className="h-12 shrink-0">
              Place bid
            </Button>
          </div>
          <div className="mt-3 grid grid-cols-4 gap-2" aria-label="Quick amounts">
            {RAISES.map((r) => (
              <Button
                key={r}
                type="button"
                variant="ghost"
                className="min-h-9 px-1 text-sm whitespace-nowrap"
                onClick={() => setAmount(String(toBeat + r))}
              >
                +{r} L
              </Button>
            ))}
          </div>
        </form>
      )}
      <ErrorText>{error}</ErrorText>
    </div>
  )
}

import { useState } from 'react'
import { api } from '../lib/api'
import { money } from '../lib/format'
import { Button, ErrorText } from './ui'

export default function AuctioneerPanel({ auction }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { player, bids } = auction
  const top = bids[0]

  // a confirm dialog is enough to stop a misclick
  async function run(action, question) {
    if (!window.confirm(question)) return
    setBusy(true)
    setError('')
    try {
      await action()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-6 rounded-2xl bg-paper p-4 sm:p-5">
      <h3 className="mb-3 font-display text-base font-semibold">Auctioneer</h3>
      {!player ? (
        <p className="text-slate">Choose a player from the pool and press Start to open bidding.</p>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2">
          <Button
            disabled={busy || !top}
            onClick={() =>
              run(() => api.accept(top.id), `Sell ${player.name} to ${top.team_name} for ${money(top.amount)}?`)
            }
          >
            {top ? `Sell for ${money(top.amount)}` : 'No bids to accept yet'}
          </Button>
          <Button
            variant="danger"
            disabled={busy}
            onClick={() => run(api.reject, `Reject this round? ${player.name} goes back to the pool unsold.`)}
          >
            Reject round
          </Button>
        </div>
      )}
      <ErrorText>{error}</ErrorText>
    </div>
  )
}

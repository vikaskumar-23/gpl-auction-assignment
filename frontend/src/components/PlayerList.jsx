import { useState } from 'react'
import { api } from '../lib/api'
import { money } from '../lib/format'
import { Button, ErrorText, Panel, SkillTag } from './ui'

export default function PlayerList({ players, canStart, auctionActive, className = '' }) {
  const [error, setError] = useState('')
  const available = players.filter((p) => p.status === 'available')

  async function start(player) {
    setError('')
    try {
      await api.start(player.id)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <Panel
      id="pool-title"
      title="Player pool"
      aside={<span className="text-sm text-slate">{available.length} unsold</span>}
      className={`@container ${className}`}
    >
      <ErrorText>{error}</ErrorText>
      {canStart && auctionActive && (
        <p className="mb-3 text-sm text-slate">Sell or reject the current player to start the next one.</p>
      )}
      {available.length === 0 ? (
        <p className="text-slate">Every player has been sold.</p>
      ) : (
        <ul className="grid gap-3 @lg:grid-cols-2 @3xl:grid-cols-3 @5xl:grid-cols-4">
          {available.map((p) => (
            <li key={p.id} className="flex flex-col gap-3 rounded-2xl border border-line p-4">
              <div className="min-w-0">
                <p className="truncate font-semibold">{p.name}</p>
                <p className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-slate">
                  <SkillTag skill={p.skill} />
                  Base {money(p.base_price)}
                </p>
              </div>
              {canStart && !auctionActive && (
                <Button variant="ghost" className="mt-auto w-full" onClick={() => start(p)}>
                  Start
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
    </Panel>
  )
}

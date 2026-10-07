import { money } from '../lib/format'
import { BidPaddle, Paddle, SkillTag } from './ui'

// role panels (bid box, auctioneer controls) come in as children, right under the price
export default function AuctionStage({ auction, className = '', children }) {
  const { player, bids } = auction
  const top = bids[0]

  return (
    <section
      aria-labelledby="stage-title"
      className={`@container rounded-[24px] border border-line bg-card p-5 shadow-[0_18px_40px_-28px_rgba(18,24,38,0.45)] sm:p-6 ${className}`}
    >
      <h2 id="stage-title" className="text-sm font-medium text-slate">
        On the block
      </h2>

      {!player ? (
        <>
          <p className="mt-2 font-display text-xl font-semibold">No player on the block yet</p>
          {children}
        </>
      ) : (
        <>
          {/* side by side only when the stage is wide enough */}
          <div className="mt-2 grid gap-5 @2xl:grid-cols-[minmax(0,1fr)_auto] @2xl:items-end">
            <div className="min-w-0">
              <p className="font-display text-3xl font-bold leading-tight break-words @md:text-4xl @5xl:text-5xl">
                {player.name}
              </p>
              <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-slate">
                <SkillTag skill={player.skill} />
                Base price {money(player.base_price)}
              </p>
            </div>
            <div aria-live="polite">
              {top ? (
                <BidPaddle key={top.id} bid={top} />
              ) : (
                <div className="rounded-2xl border-2 border-dashed border-line px-5 py-4 text-slate @2xl:min-w-64">
                  <p className="font-semibold text-ink">No bids yet</p>
                  <p className="text-sm">The opening bid must beat {money(player.base_price)}.</p>
                </div>
              )}
            </div>
          </div>

          {children}

          {bids.length > 0 && (
            <div className="mt-6">
              <h3 className="mb-1 text-sm font-medium text-slate">Bids this round ({bids.length})</h3>
              <ol className="max-h-72 overflow-y-auto">
                {bids.map((b, i) => (
                  <li
                    key={b.id}
                    className="flex items-center justify-between gap-3 border-t border-line py-2 first:border-t-0"
                  >
                    <span className="flex min-w-0 items-center gap-2.5">
                      <Paddle teamId={b.team_id} />
                      <span className="truncate">{b.team_name}</span>
                    </span>
                    <span className="flex shrink-0 items-baseline gap-3 tabular-nums">
                      <time dateTime={b.created_at} className="hidden text-xs text-slate min-[400px]:inline">
                        {new Date(b.created_at).toLocaleTimeString()}
                      </time>
                      <span className={`font-semibold ${i === 0 ? '' : 'text-slate'}`}>{money(b.amount)}</span>
                    </span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </>
      )}
    </section>
  )
}

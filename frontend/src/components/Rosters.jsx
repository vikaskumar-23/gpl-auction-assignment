import { money, SKILL_LABEL, teamColor } from '../lib/format'
import { Paddle } from './ui'

function TeamSheet({ team, mine }) {
  const left = (team.remaining_budget / team.total_budget) * 100
  return (
    <article className={`px-5 py-4 ${mine ? 'bg-paper' : ''}`}>
      <header className="flex items-center justify-between gap-2">
        <h3 className="flex min-w-0 items-center gap-2.5 font-semibold">
          <Paddle teamId={team.id} />
          <span className="truncate">{team.name}</span>
          {mine && (
            <span className="shrink-0 rounded-full bg-ink px-2 py-0.5 text-[11px] font-semibold text-paper">
              Your team
            </span>
          )}
        </h3>
        <span className="shrink-0 text-sm text-slate">
          {team.players.length} {team.players.length === 1 ? 'player' : 'players'}
        </span>
      </header>
      <p className="mt-2 text-sm">
        <span className="font-semibold tabular-nums">{money(team.remaining_budget)}</span>
        <span className="text-slate"> left of {money(team.total_budget)}</span>
      </p>
      <div
        role="progressbar"
        aria-label={`${team.name} budget left`}
        aria-valuemin={0}
        aria-valuemax={team.total_budget}
        aria-valuenow={team.remaining_budget}
        className="mt-2 h-2 overflow-hidden rounded-full bg-line"
      >
        <div className="h-full rounded-full" style={{ width: `${left}%`, backgroundColor: teamColor(team.id) }} />
      </div>
      {team.players.length > 0 && (
        <ul className="mt-3 space-y-1.5 text-sm">
          {team.players.map((p) => (
            <li key={p.id} className="flex items-baseline justify-between gap-2">
              <span className="min-w-0 truncate">
                {p.name} <span className="text-slate">({SKILL_LABEL[p.skill]})</span>
              </span>
              <span className="shrink-0 font-semibold tabular-nums">{money(p.sold_price)}</span>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}

// sticky on desktop so budgets stay in view
export default function Rosters({ teams, myTeamId, className = '' }) {
  return (
    <section
      aria-labelledby="team-sheets"
      className={`overflow-hidden rounded-[20px] border border-line bg-card lg:sticky lg:top-20 lg:max-h-[calc(100dvh-6rem)] lg:overflow-y-auto ${className}`}
    >
      <h2 id="team-sheets" className="px-5 pt-5 pb-1 font-display text-lg font-semibold">
        Team sheets
      </h2>
      <div className="divide-y divide-line">
        {teams.map((t) => (
          <TeamSheet key={t.id} team={t} mine={t.id === myTeamId} />
        ))}
      </div>
    </section>
  )
}

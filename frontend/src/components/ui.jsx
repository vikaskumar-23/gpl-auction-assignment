import { money, SKILL_LABEL, teamColor } from '../lib/format'

const FOCUS = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cobalt'

export function Panel({ id, title, aside, className = '', children }) {
  return (
    <section aria-labelledby={id} className={`rounded-[20px] border border-line bg-card ${className}`}>
      <header className="flex items-baseline justify-between gap-3 px-5 pt-5">
        <h2 id={id} className="font-display text-lg font-semibold">
          {title}
        </h2>
        {aside}
      </header>
      <div className="p-5">{children}</div>
    </section>
  )
}

const BUTTON = {
  primary: 'bg-ink text-paper hover:opacity-90',
  ghost: 'border border-line bg-card text-ink hover:border-slate',
  danger: 'border border-danger/60 text-danger hover:bg-danger/10',
}

export function Button({ variant = 'primary', className = '', ...props }) {
  return (
    <button
      className={`min-h-11 rounded-xl px-4 font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${FOCUS} ${BUTTON[variant]} ${className}`}
      {...props}
    />
  )
}

export function SkillTag({ skill }) {
  return (
    <span className="rounded-full border border-line bg-paper px-2.5 py-0.5 text-xs font-medium text-slate">
      {SKILL_LABEL[skill]}
    </span>
  )
}

// small numbered team badge
export function Paddle({ teamId }) {
  return (
    <span
      aria-hidden
      className="grid size-6 shrink-0 place-items-center rounded-md text-xs font-bold text-white"
      style={{ backgroundColor: teamColor(teamId) }}
    >
      {teamId}
    </span>
  )
}

// keyed by bid id in AuctionStage, so it animates on every new lead
export function BidPaddle({ bid }) {
  return (
    <div
      className="paddle-raise rounded-2xl px-5 py-4 text-white @2xl:min-w-64"
      style={{ backgroundColor: teamColor(bid.team_id) }}
    >
      <p className="flex items-center gap-2 text-sm font-semibold">
        <span aria-hidden className="grid size-6 place-items-center rounded-md bg-white/20 text-xs">
          {bid.team_id}
        </span>
        {bid.team_name} lead
      </p>
      <p className="mt-2 font-display text-4xl font-bold tabular-nums @md:text-5xl">{money(bid.amount)}</p>
    </div>
  )
}

export function ErrorText({ children }) {
  if (!children) return null
  return (
    <p role="alert" className="mt-3 rounded-xl border border-danger/40 bg-danger/10 px-3 py-2 text-sm">
      {children}
    </p>
  )
}

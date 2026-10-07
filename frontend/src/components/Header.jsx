export default function Header({ who, connected, onSwitch }) {
  return (
    <header className="sticky top-0 z-10 border-b border-line bg-paper/85 backdrop-blur">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <span
            aria-hidden
            className="grid size-9 shrink-0 place-items-center rounded-xl bg-ink font-display text-[11px] font-bold text-paper"
          >
            GPL
          </span>
          {/* phones show only the role line */}
          <div className="min-w-0">
            <p className="hidden font-display text-sm font-semibold leading-tight sm:block">Player Auction</p>
            <p className="truncate text-sm font-semibold sm:font-normal sm:text-slate">{who}</p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span
            aria-live="polite"
            className="flex items-center gap-1.5 rounded-full border border-line px-2.5 py-1 text-xs font-medium"
          >
            <span className={`size-2 rounded-full ${connected ? 'bg-ok' : 'bg-danger'}`} />
            {connected ? 'Live' : 'Reconnecting…'}
          </span>
          <button
            onClick={onSwitch}
            aria-label="Switch role"
            className="rounded-full border border-line px-3 py-1.5 text-sm font-medium hover:border-slate focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cobalt"
          >
            Switch<span className="hidden sm:inline"> role</span>
          </button>
        </div>
      </div>
    </header>
  )
}

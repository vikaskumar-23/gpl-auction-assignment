import { Paddle } from './ui'

function RoleOption({ title, subtitle, teamId, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-2xl border border-line bg-card p-4 text-left transition hover:border-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cobalt"
    >
      {teamId && <Paddle teamId={teamId} />}
      <span className="min-w-0">
        <span className="block font-semibold">{title}</span>
        <span className="block text-sm text-slate">{subtitle}</span>
      </span>
    </button>
  )
}

function Group({ label, children }) {
  return (
    <div className="space-y-2">
      <h2 className="text-sm font-medium text-slate">{label}</h2>
      {children}
    </div>
  )
}

export default function RolePicker({ teams, onChoose }) {
  return (
    <main className="mx-auto max-w-2xl px-4 py-12 sm:py-16">
      <header className="mb-10">
        <span
          aria-hidden
          className="mb-6 grid size-12 place-items-center rounded-2xl bg-ink font-display text-sm font-bold text-paper"
        >
          GPL
        </span>
        <h1 className="font-display text-3xl font-bold leading-tight sm:text-4xl">Player Auction</h1>
        <p className="mt-3 text-slate">
          IIT Goa Premier League. Choose how you are joining; there is no password in this demo.
        </p>
      </header>
      <div className="space-y-8">
        <Group label="Run the room">
          <RoleOption
            title="Auctioneer"
            subtitle="Put players up, then sell to the highest bid or reject the round"
            onClick={() => onChoose({ role: 'auctioneer' })}
          />
        </Group>
        <Group label="Bid for a team">
          <div className="grid gap-2 sm:grid-cols-2">
            {teams.map((t) => (
              <RoleOption
                key={t.id}
                teamId={t.id}
                title={t.name}
                subtitle="Team manager"
                onClick={() => onChoose({ role: 'manager', teamId: t.id })}
              />
            ))}
          </div>
        </Group>
        <Group label="Just watching">
          <RoleOption
            title="Spectator"
            subtitle="Follow the bids and team sheets"
            onClick={() => onChoose({ role: 'viewer' })}
          />
        </Group>
      </div>
    </main>
  )
}

import { useLiveState } from './lib/useLiveState'

export default function App() {
  const { state, connected } = useLiveState()
  if (!state) return <p className="p-4 text-slate-400">Connecting to the auction…</p>
  return (
    <p className="p-4">
      {connected ? 'Live' : 'Reconnecting'} — {state.players.length} players, {state.teams.length} teams
    </p>
  )
}

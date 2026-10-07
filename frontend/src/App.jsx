import { useState } from 'react'
import AuctioneerPanel from './components/AuctioneerPanel'
import AuctionStage from './components/AuctionStage'
import BidBox from './components/BidBox'
import Header from './components/Header'
import PlayerList from './components/PlayerList'
import Rosters from './components/Rosters'
import RolePicker from './components/RolePicker'
import { loadSession, saveSession } from './lib/session'
import { useLiveState } from './lib/useLiveState'

export default function App() {
  const { state, connected } = useLiveState()
  const [session, setSession] = useState(loadSession)

  function choose(next) {
    saveSession(next)
    setSession(next)
  }

  if (!state) {
    return <p className="grid min-h-dvh place-items-center text-slate">Connecting to the auction…</p>
  }

  const myTeam = session?.role === 'manager' ? state.teams.find((t) => t.id === session.teamId) : null
  if (!session || (session.role === 'manager' && !myTeam)) {
    return <RolePicker teams={state.teams} onChoose={choose} />
  }

  const who =
    session.role === 'auctioneer' ? 'Running the auction' : myTeam ? `Managing ${myTeam.name}` : 'Watching as a spectator'

  return (
    <div className="min-h-dvh">
      <Header who={who} connected={connected} onSwitch={() => choose(null)} />
      {/* one column on phones and tablets; board + team sheets side by side on desktop */}
      <main className="mx-auto grid max-w-[1600px] items-start gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[minmax(0,1fr)_minmax(320px,400px)] lg:py-8">
        <div className="grid min-w-0 gap-5">
          <AuctionStage auction={state.auction}>
            {/* keyed by player so the box resets for each new player */}
            {myTeam && <BidBox key={state.auction.player?.id ?? 'idle'} team={myTeam} auction={state.auction} />}
            {session.role === 'auctioneer' && (
              <AuctioneerPanel key={state.auction.player?.id ?? 'idle'} auction={state.auction} />
            )}
          </AuctionStage>
          <PlayerList
            players={state.players}
            canStart={session.role === 'auctioneer'}
            auctionActive={!!state.auction.player}
          />
        </div>
        <Rosters teams={state.teams} myTeamId={myTeam?.id} />
      </main>
    </div>
  )
}

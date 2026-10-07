import { useEffect, useState } from 'react'

// the server pings every 15s when idle; 40s of silence means the connection died
// without EventSource noticing (e.g. a wifi switch)
const STALL_MS = 40_000

// full auction state arrives on connect and after every change
export function useLiveState() {
  const [state, setState] = useState(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let source
    let stallTimer

    function heard() {
      setConnected(true)
      clearTimeout(stallTimer)
      stallTimer = setTimeout(() => {
        setConnected(false)
        source.close()
        open()
      }, STALL_MS)
    }

    function open() {
      source = new EventSource('/api/events')
      source.addEventListener('state', (e) => {
        setState(JSON.parse(e.data))
        heard()
      })
      source.addEventListener('ping', heard)
      source.onerror = () => setConnected(false) // EventSource retries on its own
    }

    open()
    return () => {
      clearTimeout(stallTimer)
      source.close()
    }
  }, [])

  return { state, connected }
}

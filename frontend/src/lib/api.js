export class ApiError extends Error {
  constructor(message, code) {
    super(message)
    this.code = code
  }
}

async function post(path, role, body) {
  let res
  try {
    res = await fetch(`/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Role': role },
      body: body && JSON.stringify(body),
    })
  } catch {
    throw new ApiError("Can't reach the auction server. Check your connection and try again.", 'NETWORK')
  }
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(data?.error?.message ?? `Request failed (${res.status}).`, data?.error?.code)
  return data
}

export const api = {
  start: (playerId) => post('/auction/start', 'auctioneer', { player_id: playerId }),
  bid: (teamId, amount) => post('/auction/bids', 'manager', { team_id: teamId, amount }),
  accept: (bidId) => post('/auction/accept', 'auctioneer', { bid_id: bidId }),
  reject: () => post('/auction/reject', 'auctioneer'),
}

// amounts are in lakh: 75 -> ₹75 L, 150 -> ₹1.5 Cr
export function money(lakh) {
  return lakh >= 100 ? `₹${+(lakh / 100).toFixed(2)} Cr` : `₹${lakh} L`
}

export const SKILL_LABEL = { batting: 'Batter', bowling: 'Bowler', both: 'All-rounder' }

// dark enough for white text in both themes
const TEAM_COLORS = ['#cc2f38', '#a85a00', '#137a50', '#6e56cf']
export const teamColor = (teamId) => TEAM_COLORS[(teamId - 1) % TEAM_COLORS.length]

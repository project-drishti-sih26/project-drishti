/**
 * Markers Utility (Role 3 - GIS)
 * Generates custom high-contrast radar markers for predicted cashout points:
 * - Rank #1: Pulsing red beacon with concentric ripple waves
 * - Rank #2-5: Orange/amber glow beacons
 */

export const renderCustomMarker = (atm, rank = 1, isSelected = false) => {
  const el = document.createElement('div');
  el.className = 'cursor-pointer select-none';

  if (rank === 1) {
    // Rank #1: Intense Red Radar Beacon
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <span class="absolute w-12 h-12 rounded-full bg-red-500/30 animate-ping"></span>
        <span class="absolute w-8 h-8 rounded-full bg-red-600/50 animate-pulse"></span>
        <div class="relative z-10 flex items-center justify-center w-7 h-7 bg-red-600 border-2 border-white rounded-full text-white font-bold text-xs shadow-lg shadow-red-500/50">
          #1
        </div>
      </div>
    `;
  } else {
    // Rank #2-5: Amber/Orange Beacon
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <span class="absolute w-7 h-7 rounded-full bg-amber-500/20 animate-pulse"></span>
        <div class="relative z-10 flex items-center justify-center w-6 h-6 bg-amber-500 border border-slate-900 rounded-full text-slate-950 font-bold text-[10px] shadow-md shadow-amber-500/30">
          #${rank}
        </div>
      </div>
    `;
  }

  if (isSelected) {
    el.firstElementChild?.classList.add('ring-4', 'ring-cyan-400');
  }

  return el;
};

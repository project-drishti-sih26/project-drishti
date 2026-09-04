/**
 * Markers Generator (Role 3 - GIS Radar)
 * Project Drishti - Tactical Map Visualizer
 * 
 * Flat, hard-edged solid markers with clear rank numbers:
 * - Rank #1: Solid Red
 * - Rank #2-3: Solid Amber
 * - Rank #4+: Solid Slate / Grey
 * No soft glowing rings, no pulse animation halos.
 */

export const renderCustomMarker = (location, rank = 1, isSelected = false) => {
  const el = document.createElement('div');
  el.className = 'gis-radar-marker group cursor-pointer select-none';
  el.setAttribute('data-id', location.id || `loc-${rank}`);
  el.setAttribute('title', `${location.name || 'ATM Node'} (#${rank})`);

  const isTopRank = rank === 1;
  const isHighRank = rank <= 3;

  let bgClasses = 'bg-slate-700 text-slate-200 border border-slate-600';
  if (isTopRank) {
    bgClasses = 'bg-rose-700 text-white border border-rose-900';
  } else if (isHighRank) {
    bgClasses = 'bg-amber-600 text-white border border-amber-800';
  }

  const selectedRing = isSelected ? 'ring-2 ring-slate-900 ring-offset-1 shadow-sm' : '';

  el.innerHTML = `
    <div class="relative flex flex-col items-center">
      <!-- Flat Hard-edged Solid Rank Marker -->
      <div class="w-6 h-6 rounded-[3px] flex items-center justify-center font-mono font-medium text-[11px] ${bgClasses} ${selectedRing}">
        #${rank}
      </div>
      <!-- Pointer Tip -->
      <div class="w-1.5 h-1.5 -mt-0.5 rotate-45 ${isTopRank ? 'bg-rose-700' : isHighRank ? 'bg-amber-600' : 'bg-slate-700'}"></div>
    </div>
  `;

  return el;
};

export default renderCustomMarker;

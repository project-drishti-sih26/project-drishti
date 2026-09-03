/**
 * Markers Generator (Role 3 - GIS Radar)
 * Project Drishti - Tactical Map Visualizer
 * 
 * Generates custom DOM markers for predicted cashout points:
 * - ATM: Automated Teller Machine (Terminal Icon)
 * - Bank Branch: Physical Bank Office (Building/Vault Icon)
 * - BC Point: Business Correspondent / CSP Point (Kiosk/User Icon)
 * 
 * High-contrast tactical radar indicators:
 * - Rank #1: Critical pulsating Red radar beacon with radiating ping waves
 * - Rank #2-3: High risk Amber/Orange glowing pins
 * - Rank #4+: Medium/Low risk Cyan/Slate badges
 */

export const renderCustomMarker = (location, rank = 1, isSelected = false) => {
  const el = document.createElement('div');
  el.className = 'gis-radar-marker group cursor-pointer select-none transition-transform duration-200 hover:scale-110';
  el.setAttribute('data-id', location.id || `loc-${rank}`);
  el.setAttribute('title', `${location.name || 'Target'} (#${rank})`);

  const type = location.type || 'ATM';
  const isTopRank = rank === 1;

  // Type badge label abbreviations
  let typeAbbr = 'ATM';
  let typeColor = 'bg-red-500 text-white';
  if (type.toLowerCase().includes('branch')) {
    typeAbbr = 'BNK';
    typeColor = 'bg-blue-500 text-white';
  } else if (type.toLowerCase().includes('bc') || type.toLowerCase().includes('point')) {
    typeAbbr = 'BC';
    typeColor = 'bg-emerald-500 text-slate-950 font-black';
  }

  // Visual styling based on rank and type
  if (isTopRank) {
    // Rank #1: Critical Intense Red Pulsing Beacon
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <!-- Outward radiating radar ping wave -->
        <span class="absolute w-14 h-14 rounded-full bg-red-500/30 animate-ping pointer-events-none"></span>
        <span class="absolute w-10 h-10 rounded-full bg-red-600/40 animate-pulse pointer-events-none"></span>
        
        <!-- Main Marker Circle -->
        <div class="relative z-10 flex flex-col items-center justify-center w-9 h-9 bg-gradient-to-b from-red-500 to-red-700 border-2 border-white rounded-full shadow-[0_0_15px_rgba(239,68,68,0.8)]">
          <span class="text-white font-black text-[11px] leading-none">#1</span>
          <span class="text-[7px] font-mono tracking-tighter text-red-100 uppercase font-semibold">${typeAbbr}</span>
        </div>

        <!-- Tactical Pin Pointer -->
        <div class="absolute -bottom-1 z-0 w-2 h-2 bg-red-600 rotate-45 border-r border-b border-white"></div>
      </div>
    `;
  } else if (rank <= 3) {
    // Rank #2-3: High Risk Amber Beacon
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <span class="absolute w-8 h-8 rounded-full bg-amber-500/25 animate-pulse pointer-events-none"></span>
        
        <div class="relative z-10 flex flex-col items-center justify-center w-8 h-8 bg-gradient-to-b from-amber-400 to-amber-600 border border-slate-900 rounded-full shadow-[0_0_10px_rgba(245,158,11,0.6)]">
          <span class="text-slate-950 font-black text-[10px] leading-none">#${rank}</span>
          <span class="text-[7px] font-mono tracking-tighter text-slate-900 font-bold uppercase">${typeAbbr}</span>
        </div>
      </div>
    `;
  } else {
    // Rank #4+: Medium/Low Risk Cyan/Slate Marker
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <div class="relative z-10 flex flex-col items-center justify-center w-7 h-7 bg-slate-800/90 border border-cyan-500/60 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.4)] backdrop-blur-sm">
          <span class="text-cyan-300 font-bold text-[10px] leading-none">#${rank}</span>
          <span class="text-[6px] font-mono text-cyan-400 font-semibold uppercase">${typeAbbr}</span>
        </div>
      </div>
    `;
  }

  // Active selection highlight effect
  if (isSelected) {
    const container = el.firstElementChild;
    if (container) {
      container.classList.add('scale-125');
      const innerBadge = container.querySelector('.relative.z-10');
      if (innerBadge) {
        innerBadge.classList.add('ring-4', 'ring-cyan-300', 'ring-offset-2', 'ring-offset-slate-950');
      }
    }
  }

  return el;
};

export default renderCustomMarker;

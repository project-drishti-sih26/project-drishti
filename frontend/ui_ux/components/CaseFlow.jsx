import React from 'react';

/**
 * CaseFlow Component (Role 4 - UI/UX)
 * Transaction Trail: 01. Victim Account -> 02. Mule Account (Hop 1) -> 03. Predicted Withdrawal Location
 */
const CaseFlow = ({
  victim = 'SBIN •••• 9284',
  victimName = 'R. K. Sharma',
  victimBank = 'State Bank of India (Connaught Place Branch)',
  mule = 'HDFC •••• 9201',
  muleName = 'Imran Ansari',
  muleBank = 'HDFC Bank (Noida Sector 18 Branch)',
  predictedAtm = 'SBI Kiosk #091, Inner Circle Block-B, CP',
  predictedEta = null,
  predictedDistance = null,
  assignedPatrol = 'PCR Unit 12 (Central Division)'
}) => {
  // Was hardcoded "ETA: ~11 min (1.8 km)". On a live alert the model's rank-1
  // target was 5 min / 2.12 km, so the case trail contradicted the ranked list
  // sitting beside it on the same screen.
  const etaLine = (predictedEta || predictedDistance)
    ? `ETA: ~${predictedEta || '?'}${predictedDistance ? ` (${predictedDistance})` : ''}`
    : null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
      <div className="bg-slate-50 border border-slate-200 rounded-sm p-3">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">01. Victim Account</span>
        <div className="font-semibold text-slate-900 text-xs mt-1">{victimName}</div>
        <div className="font-mono text-xs text-slate-600 mt-0.5">{victim}</div>
        <div className="text-xs text-slate-500 mt-1">{victimBank}</div>
      </div>

      <div className="bg-rose-50/60 border border-rose-200 rounded-sm p-3">
        <span className="text-xs font-bold text-rose-800 uppercase tracking-wider block">02. Mule Account (Hop 1)</span>
        <div className="font-semibold text-rose-950 text-xs mt-1">{muleName}</div>
        <div className="font-mono text-xs text-rose-800 font-bold mt-0.5">{mule}</div>
        <div className="text-xs text-rose-700 mt-1">{muleBank}</div>
      </div>

      <div className="bg-slate-100/80 border border-slate-300 rounded-sm p-3">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">03. Predicted Withdrawal Location</span>
        <div className="font-semibold text-slate-900 text-xs mt-1">{predictedAtm}</div>
        {etaLine && (
          <div className="text-xs text-slate-700 font-semibold mt-0.5">{etaLine}</div>
        )}
        <div className="text-xs text-slate-600 mt-1">{assignedPatrol}</div>
      </div>
    </div>
  );
};

export default CaseFlow;

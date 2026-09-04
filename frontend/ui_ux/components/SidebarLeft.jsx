import React from 'react';
import CaseFlow from './CaseFlow';

/**
 * SidebarLeft Component (Role 4 - UI/UX)
 * Incident Record & Transaction Trail
 */
const SidebarLeft = ({
  caseData = {
    case_id: 'NCR-2026-00491',
    victim_name: 'R. K. Sharma',
    victim_account: 'SBIN •••• 9284',
    victim_bank: 'State Bank of India (Connaught Place Branch)',
    mule_account: 'HDFC •••• 9201',
    mule_name: 'Imran Ansari',
    mule_bank: 'HDFC Bank (Noida Sector 18 Branch)',
    compromised_amount: 85000,
    debit_time: '22:41 IST',
    crime_vector: 'Unauthorized APK Screen Share',
    predicted_atm: 'SBI Kiosk #091, Inner Circle Block-B, CP',
    assigned_patrol: 'PCR Unit 12 (Central Division)'
  }
}) => {
  return (
    <div className="bg-white rounded-sm border border-slate-200 p-4 space-y-3">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Incident Record</h2>
            <span className="px-1.5 py-0.5 rounded-sm text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-200">
              {caseData.case_id}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">Method: {caseData.crime_vector} • Logged at {caseData.debit_time}</p>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-slate-400 block uppercase">Reported Amount</span>
          <span className="text-base font-bold text-slate-900 font-mono">
            ₹{Number(caseData.compromised_amount).toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      <CaseFlow
        victim={caseData.victim_account}
        victimName={caseData.victim_name}
        victimBank={caseData.victim_bank}
        mule={caseData.mule_account}
        muleName={caseData.mule_name}
        muleBank={caseData.mule_bank}
        predictedAtm={caseData.predicted_atm}
        predictedEta={caseData.predicted_eta}
        predictedDistance={caseData.predicted_distance}
        assignedPatrol={caseData.assigned_patrol}
      />
    </div>
  );
};

export default SidebarLeft;

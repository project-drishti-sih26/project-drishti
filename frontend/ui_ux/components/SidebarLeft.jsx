import React from 'react';
import CaseFlow from './CaseFlow';

/**
 * SidebarLeft Component
 * Center Column Dossier for Live Incidents:
 * 1. Incident Record Summary Card (Victim / Mule / Predicted Node)
 * 2. Transaction Trail (Account-hop graph with transfer amount & timing)
 * 3. Case Timeline (Chronological operational audit log)
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
    assigned_patrol: 'PCR Unit 12 (Central Division)',
    status: 'Active'
  }
}) => {
  // Generate realistic, case-specific operational timeline milestones
  const getTimelineEvents = (c) => {
    const baseTime = c.debit_time || '22:41 IST';
    const match = baseTime.match(/(\d{1,2}):(\d{2})/);
    let h = 22, m = 41;
    if (match) {
      h = parseInt(match[1], 10);
      m = parseInt(match[2], 10);
    }

    const formatTime = (addMins) => {
      const totalM = h * 60 + m + addMins;
      const newH = Math.floor((totalM % (24 * 60)) / 60);
      const newM = totalM % 60;
      return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')} IST`;
    };

    return [
      {
        time: formatTime(0),
        title: 'Complaint Registered',
        desc: `Victim ${c.victim_name || 'Citizen'} reported unauthorized debit via 1930 / I4C portal (${c.crime_vector || 'Cyber Fraud'}).`,
        status: 'done'
      },
      {
        time: formatTime(2),
        title: 'Mule Account Flagged',
        desc: `First-hop beneficiary account identified at ${c.mule_bank || 'Beneficiary Bank'} (${c.mule_account || 'Mule Acc'}).`,
        status: 'done'
      },
      {
        time: formatTime(3),
        title: 'Spatial Prediction Generated',
        desc: `Case analysis identified ${c.predicted_atm?.split(',')[0] || 'Target ATM'} as priority withdrawal location (Confidence: 89%).`,
        status: 'done'
      },
      {
        time: formatTime(4),
        title: 'Field Patrol Dispatched',
        desc: `Operational alert and intercept coordinates routed to ${c.assigned_patrol || 'PCR Unit 12'}.`,
        status: 'done'
      },
      {
        time: formatTime(7),
        title: 'Section 91 Notice Prepared',
        desc: `Automated Section 91 CrPC compliance order pre-generated for nodal bank compliance officer.`,
        status: 'done'
      },
      {
        time: c.status === 'Resolved' ? formatTime(34) : 'Active',
        title: c.status === 'Resolved' ? 'Case Resolved' : 'Interception In Progress',
        desc: c.status === 'Resolved'
          ? `Funds successfully restrained at beneficiary branch; debit restriction enforced.`
          : `Awaiting field patrol verification and bank debit restriction confirmation.`,
        status: c.status === 'Resolved' ? 'done' : 'active'
      }
    ];
  };

  const timelineEvents = getTimelineEvents(caseData);

  return (
    <div className="space-y-3.5 select-none">
      {/* 1. INCIDENT RECORD CARD */}
      <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-medium text-slate-900 uppercase">Incident Record</h2>
              <span className="text-[11px] font-mono font-medium px-1.5 py-0.5 rounded-[3px] bg-slate-100 text-slate-700 border border-slate-200">
                {caseData.case_id}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal mt-0.5">
              Method: {caseData.crime_vector} • Logged {caseData.debit_time}
            </p>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-slate-400 font-normal block uppercase">Reported</span>
            <span className="text-sm font-medium text-slate-900 font-mono">
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
          assignedPatrol={caseData.assigned_patrol}
        />
      </div>

      {/* 2. TRANSACTION TRAIL (HOP GRAPH) */}
      <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 className="text-xs font-medium text-slate-900 uppercase">
              Transaction Trail (Hop Graph)
            </h3>
            <p className="text-[11px] text-slate-400 font-normal mt-0.5">
              Account-to-account flow & physical cashout routing
            </p>
          </div>
          <span className="text-[11px] font-mono font-medium px-1.5 py-0.5 rounded-[3px] bg-slate-100 text-slate-700 border border-slate-200">
            1 Hop Identified
          </span>
        </div>

        {/* Directed Hop Graph Nodes */}
        <div className="space-y-2 text-xs">
          {/* Node 1: Victim Account (Origin) */}
          <div className="p-2.5 bg-slate-50/80 rounded-[4px] border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-5 h-5 rounded-[3px] bg-slate-200 text-slate-700 flex items-center justify-center font-mono text-[10px] font-medium shrink-0">
                01
              </span>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-slate-900">{caseData.victim_name}</span>
                  <span className="text-[10px] text-slate-400 font-normal">(Victim Origin)</span>
                </div>
                <div className="text-[11px] text-slate-700 font-mono font-medium">{caseData.victim_account}</div>
                <div className="text-[11px] text-slate-500 font-normal">{caseData.victim_bank}</div>
              </div>
            </div>
          </div>

          {/* Transfer Edge Connector 1 */}
          <div className="flex items-center justify-between px-4 py-1 text-[11px] font-mono text-slate-500 bg-slate-100/50 rounded-[3px] border border-dashed border-slate-200">
            <div className="flex items-center gap-1.5 text-rose-700 font-medium">
              <span>↓ Transfer: ₹{Number(caseData.compromised_amount).toLocaleString('en-IN')}</span>
              <span className="text-slate-400 font-normal">(Instant UPI/IMPS)</span>
            </div>
            <span className="text-slate-400 font-normal">{caseData.debit_time}</span>
          </div>

          {/* Node 2: Mule Account (Hop 1) */}
          <div className="p-2.5 bg-rose-50/50 rounded-[4px] border border-rose-200 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-5 h-5 rounded-[3px] bg-rose-100 text-rose-800 border border-rose-200 flex items-center justify-center font-mono text-[10px] font-medium shrink-0">
                02
              </span>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-slate-900">{caseData.mule_name}</span>
                  <span className="text-[10px] text-rose-700 font-medium">(Hop 1 Mule)</span>
                </div>
                <div className="text-[11px] text-rose-800 font-mono font-medium">{caseData.mule_account}</div>
                <div className="text-[11px] text-slate-600 font-normal">{caseData.mule_bank}</div>
              </div>
            </div>
          </div>

          {/* Transfer Edge Connector 2 */}
          <div className="flex items-center justify-between px-4 py-1 text-[11px] font-mono text-slate-500 bg-slate-100/50 rounded-[3px] border border-dashed border-slate-200">
            <div className="flex items-center gap-1.5 text-slate-700 font-medium">
              <span>↓ Estimated withdrawal window: ~11 min</span>
            </div>
            <span className="text-slate-400 font-normal">Rank #1</span>
          </div>

          {/* Node 3: Predicted ATM Node (Terminal) */}
          <div className="p-2.5 bg-slate-100/70 rounded-[4px] border border-slate-300 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-5 h-5 rounded-[3px] bg-slate-900 text-white flex items-center justify-center font-mono text-[10px] font-medium shrink-0">
                03
              </span>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-slate-900">{caseData.predicted_atm}</span>
                  <span className="text-[10px] text-slate-500 font-normal">(Terminal)</span>
                </div>
                <div className="text-[11px] text-slate-600 font-normal">
                  Assigned Patrol: <strong className="text-slate-800 font-medium">{caseData.assigned_patrol}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default SidebarLeft;

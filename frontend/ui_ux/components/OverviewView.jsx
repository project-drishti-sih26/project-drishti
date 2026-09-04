import React from 'react';

/**
 * OverviewView Component
 * Clean, minimal command summary for Project Drishti.
 * Shows system-wide telemetry, single most urgent alert banner, active cases table, and incident distribution trends.
 */
const OverviewView = ({
  cases = [],
  onViewCase = () => {},
  onSelectView = () => {}
}) => {
  // Identify single most urgent active case for priority banner
  const urgentCases = cases.filter((c) => c.status === 'Active' || c.status === 'In Progress');
  const mostUrgentCase = urgentCases[0] || cases[0];

  // Active cases for compact table (Active + In Progress + Under Monitoring)
  const activeCasesList = cases.filter(
    (c) => c.status === 'Active' || c.status === 'In Progress' || c.status === 'Under Monitoring'
  );

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Active':
      case 'In Progress':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'Under Monitoring':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Resolved':
      case 'Restricted':
        return 'bg-slate-100 text-slate-600 border-slate-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <div className="space-y-4 select-none">
      {/* 1. STAT SUMMARY ROW (Total Cases / Urgent / Cases Resolved / Patrol Units) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div
          onClick={() => onSelectView('cases')}
          className="bg-white p-3.5 rounded-[4px] border border-slate-200 hover:border-slate-300 transition-colors cursor-pointer"
        >
          <span className="text-xs font-normal text-slate-500 block uppercase tracking-wide">
            Total Cases
          </span>
          <div className="mt-1.5 flex items-baseline justify-between">
            <span className="text-2xl font-medium text-slate-900 font-mono">{cases.length}</span>
            <span className="text-xs text-rose-700 font-normal">
              {urgentCases.length} Urgent
            </span>
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-[4px] border border-slate-200">
          <span className="text-xs font-normal text-slate-500 block uppercase tracking-wide">
            Urgent Cases
          </span>
          <div className="mt-1.5 flex items-baseline justify-between">
            <span className="text-2xl font-medium text-rose-700 font-mono">
              {urgentCases.length}
            </span>
            <span className="text-xs text-slate-400 font-normal">Active response</span>
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-[4px] border border-slate-200">
          <span className="text-xs font-normal text-slate-500 block uppercase tracking-wide">
            Cases Resolved
          </span>
          <div className="mt-1.5 flex items-baseline justify-between">
            <span className="text-2xl font-medium text-slate-900 font-mono">18</span>
            <span className="text-xs text-slate-600 font-normal">₹31.4 L Restrained</span>
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-[4px] border border-slate-200">
          <span className="text-xs font-normal text-slate-500 block uppercase tracking-wide">
            Patrol Units
          </span>
          <div className="mt-1.5 flex items-baseline justify-between">
            <span className="text-2xl font-medium text-slate-900 font-mono">8</span>
            <span className="text-xs text-slate-500 font-normal">PCR 12 Available</span>
          </div>
        </div>
      </div>

      {/* 2. ONE PRIORITY ALERT BANNER (Single Most Urgent Active Case) */}
      {mostUrgentCase && (
        <div className="bg-rose-50/70 border border-rose-200 rounded-[4px] p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-medium px-1.5 py-0.5 rounded-[3px] bg-rose-100 text-rose-800 border border-rose-200">
                Priority Alert • {mostUrgentCase.case_id}
              </span>
              <span className="text-xs text-slate-500 font-mono font-normal">
                Reported {mostUrgentCase.debit_time}
              </span>
            </div>
            <p className="text-xs font-normal text-slate-800 mt-1">
              Unauthorized transfer of{' '}
              <strong className="font-medium font-mono text-rose-700">
                ₹{Number(mostUrgentCase.compromised_amount).toLocaleString('en-IN')}
              </strong>{' '}
              to beneficiary account ({mostUrgentCase.mule_account} - {mostUrgentCase.mule_name}). Suspect vector: {mostUrgentCase.crime_vector}.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => onViewCase(mostUrgentCase.case_id)}
              className="px-3 py-1.5 bg-rose-700 hover:bg-rose-800 text-white text-xs font-medium rounded-[3px] transition-colors cursor-pointer"
            >
              View Case
            </button>
          </div>
        </div>
      )}

      {/* 3. ACTIVE CASES LIST (Compact Table showing all active/urgent cases) */}
      <div className="bg-white rounded-[4px] border border-slate-200 overflow-hidden">
        <div className="p-3.5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-xs font-medium text-slate-900 uppercase">
              Active Incidents Queue
            </h2>
            <p className="text-xs text-slate-400 font-normal">
              Active and monitoring cases requiring field intervention
            </p>
          </div>
          <span className="text-xs font-mono font-normal text-slate-500">
            {activeCasesList.length} Active Cases
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-normal text-xs">
              <tr>
                <th className="py-2 px-3">Case ID</th>
                <th className="py-2 px-3">Victim</th>
                <th className="py-2 px-3">Mule Account</th>
                <th className="py-2 px-3 text-right">Amount</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Time / Node</th>
                <th className="py-2 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-normal">
              {activeCasesList.map((c) => (
                <tr
                  key={c.case_id}
                  onClick={() => onViewCase(c.case_id)}
                  className="hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  {/* Case ID */}
                  <td className="py-2.5 px-3 font-mono font-medium text-slate-900">
                    {c.case_id}
                  </td>

                  {/* Victim */}
                  <td className="py-2.5 px-3">
                    <div className="font-medium text-slate-900">{c.victim_name}</div>
                    <div className="text-xs text-slate-500 font-mono">{c.victim_account}</div>
                  </td>

                  {/* Mule */}
                  <td className="py-2.5 px-3">
                    <div className="font-medium text-slate-900">{c.mule_name}</div>
                    <div className="text-xs text-slate-500 font-mono">{c.mule_account}</div>
                  </td>

                  {/* Amount */}
                  <td className="py-2.5 px-3 text-right font-mono font-medium text-slate-900">
                    ₹{Number(c.compromised_amount).toLocaleString('en-IN')}
                  </td>

                  {/* Status */}
                  <td className="py-2.5 px-3">
                    <span className={`inline-block text-xs font-mono leading-none px-1.5 py-0.5 rounded-[3px] border ${getStatusBadge(c.status)}`}>
                      {c.status}
                    </span>
                  </td>

                  {/* Time / Target Node */}
                  <td className="py-2.5 px-3">
                    <div className="text-slate-800 font-normal">{c.debit_time}</div>
                    <div className="text-xs text-slate-400 truncate max-w-[180px]">
                      {c.predicted_atm.split(',')[0]}
                    </div>
                  </td>

                  {/* View Button */}
                  <td className="py-2.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onViewCase(c.case_id)}
                      className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. HOURLY INCIDENT DISTRIBUTION + FRAUD CATEGORIES BREAKDOWN */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Hourly Distribution Bar Chart */}
        <div className="lg:col-span-8 bg-white rounded-[4px] border border-slate-200 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-slate-900 text-xs uppercase">
                Hourly Incident Distribution
              </h3>
              <p className="text-xs text-slate-400 font-normal">Past 24 hours system trend</p>
            </div>
            <span className="text-xs text-slate-500 font-mono font-normal">24h Total: 24 Cases</span>
          </div>

          <div className="h-36 flex items-end justify-between gap-2 pt-3 px-1 border-b border-slate-100">
            {[
              { time: '00:00', count: 1 },
              { time: '02:00', count: 0 },
              { time: '04:00', count: 0 },
              { time: '06:00', count: 1 },
              { time: '08:00', count: 2 },
              { time: '10:00', count: 4 },
              { time: '12:00', count: 3 },
              { time: '14:00', count: 5 },
              { time: '16:00', count: 4 },
              { time: '18:00', count: 6 },
              { time: '20:00', count: 8 },
              { time: '22:00', count: 9 },
            ].map((item, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                <span className="text-xs font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  {item.count}
                </span>
                <div
                  className={`w-full transition-all ${
                    item.count >= 8 ? 'bg-rose-700' : item.count >= 4 ? 'bg-slate-700' : 'bg-slate-200'
                  }`}
                  style={{ height: `${Math.max(item.count * 10, 5)}%` }}
                />
                <span className="text-xs font-mono text-slate-400 mt-1">{item.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Fraud Categories Breakdown */}
        <div className="lg:col-span-4 bg-white rounded-[4px] border border-slate-200 p-4 space-y-3">
          <div>
            <h3 className="font-medium text-slate-900 text-xs uppercase">
              Fraud Categories
            </h3>
            <p className="text-xs text-slate-400 font-normal">System-wide incident vectors</p>
          </div>

          <div className="space-y-2.5 pt-1">
            {[
              { label: 'Screen Share APK Fraud', pct: 38, count: '9 cases', color: 'bg-rose-700' },
              { label: 'Impersonation Vishing Call', pct: 26, count: '6 cases', color: 'bg-slate-700' },
              { label: 'KYC Phishing SMS / Link', pct: 21, count: '5 cases', color: 'bg-amber-600' },
              { label: 'Card Cloning / Skimming', pct: 15, count: '4 cases', color: 'bg-slate-400' }
            ].map((type, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between text-xs font-normal">
                  <span className="text-slate-700">{type.label}</span>
                  <span className="text-slate-400 font-mono text-xs">{type.pct}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-100 rounded-[2px] overflow-hidden">
                  <div className={`h-full ${type.color}`} style={{ width: `${type.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewView;

import React from 'react';

/**
 * Alerts Component
 * Urgent Incident Notification Banner
 */
const Alerts = ({ alert, onOpenCase = () => {} }) => {
  if (!alert) return null;
  const amount = Number(alert.amount || alert.compromised_amount || 0);

  return (
    <div className="bg-rose-50/70 border border-rose-200 rounded-[4px] p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono font-medium px-1.5 py-0.5 rounded-[3px] bg-rose-100 text-rose-800 border border-rose-200">
            Urgent Incident Alert
          </span>
          <span className="text-xs text-slate-500 font-mono font-normal">Reported 12 min ago</span>
        </div>
        <p className="text-xs font-normal text-slate-800 mt-1">
          Unauthorized transfer of <strong className="font-medium font-mono text-rose-700">₹{amount.toLocaleString('en-IN')}</strong> reported to beneficiary account ({alert.mule_account || 'HDFC •••• 9201'}). Estimated withdrawal timeframe: <span className="font-mono font-medium">~{alert.countdown || '11 min'}</span>.
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onOpenCase}
          className="px-3 py-1.5 bg-rose-700 hover:bg-rose-800 text-white text-xs font-medium rounded-[3px] transition-colors cursor-pointer"
        >
          Open Incident Feed
        </button>
      </div>
    </div>
  );
};

export default Alerts;

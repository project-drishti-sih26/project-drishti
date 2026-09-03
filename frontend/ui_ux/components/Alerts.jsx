import React from 'react';

/**
 * Alerts Component (Role 4 - UI/UX)
 * Urgent Case Notification Banner (Text-only button, flat badge)
 */
const Alerts = ({ alert, onOpenCase = () => {} }) => {
  if (!alert) return null;
  const amount = Number(alert.amount || alert.compromised_amount || 0);

  return (
    <div className="bg-rose-50/80 border border-rose-200 rounded-sm p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-rose-800 bg-rose-100 border border-rose-300 px-1.5 py-0.5 rounded-sm">
            Urgent Case Notification
          </span>
          <span className="text-xs text-slate-500 font-mono">Auto-correlated 12 min ago</span>
        </div>
        <p className="text-xs font-medium text-slate-800 mt-1">
          Unauthorized debit of <strong className="font-bold text-rose-800">₹{amount.toLocaleString('en-IN')}</strong> reported to beneficiary account ({alert.mule_account || 'HDFC •••• 9201'}). Estimated withdrawal timeframe: ~{alert.countdown || '11 min'}.
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onOpenCase}
          className="px-3 py-1.5 bg-rose-700 hover:bg-rose-800 text-white text-xs font-semibold rounded-sm transition-colors cursor-pointer"
        >
          Generate Dispatch Order
        </button>
      </div>
    </div>
  );
};

export default Alerts;

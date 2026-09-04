import React from 'react';

/**
 * Alerts Component (Role 4 - UI/UX)
 * Urgent Case Notification Banner (Text-only button, flat badge)
 */
const Alerts = ({ alert, onOpenCase = () => {} }) => {
  if (!alert) return null;
  const amount = Number(alert.amount || alert.compromised_amount || 0);

  // `countdown` is MM:SS remaining. Interpolated raw into the sentence
  // "Estimated withdrawal timeframe: ~13:45" it read as a clock time — 1:45 PM
  // — directly contradicting the IST window shown elsewhere on the same screen.
  // Labelled as a duration, with the absolute IST window beside it.
  const countdown = alert.countdown || null;
  const windowIst = alert.startIst && alert.endIst
    ? `${alert.startIst}–${alert.endIst} IST`
    : null;

  return (
    <div className="bg-rose-50/80 border border-rose-200 rounded-sm p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-rose-800 bg-rose-100 border border-rose-300 px-1.5 py-0.5 rounded-sm">
            Urgent Case Notification
          </span>
          {alert.detectedAtIst && (
            <span className="text-xs text-slate-500 font-mono">
              Debit detected {alert.detectedAtIst} IST
            </span>
          )}
        </div>
        <p className="text-xs font-medium text-slate-800 mt-1">
          Unauthorized debit of <strong className="font-bold text-rose-800">₹{amount.toLocaleString('en-IN')}</strong> reported to beneficiary account ({alert.mule_account || 'HDFC •••• 9201'}).
          {windowIst
            ? <> Predicted cash-out window <strong className="font-bold">{windowIst}</strong>{countdown ? <> — <span className="font-mono">{countdown}</span> remaining.</> : '.'}</>
            : countdown ? <> Time to predicted cash-out: <span className="font-mono font-bold">{countdown}</span> (mm:ss).</> : ''}
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

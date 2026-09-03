import React, { useState } from 'react';
import { CheckCircle2, XCircle, ShieldAlert } from 'lucide-react';

/**
 * FeedbackActions Component (Role 4 - UI/UX)
 * Human-in-the-Loop buttons for police desk operators:
 * - "Confirmed Interception" -> Marks success, feeds ground truth back to ML model.
 * - "False Alarm" -> Flags false positive for model retraining.
 */
const FeedbackActions = ({ onFeedback = () => {} }) => {
  const [feedbackStatus, setFeedbackStatus] = useState(null);

  const handleAction = (status) => {
    setFeedbackStatus(status);
    onFeedback(status);
    setTimeout(() => {
      setFeedbackStatus(null);
    }, 4000);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 select-none">
      <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
          HUMAN-IN-THE-LOOP FEEDBACK
        </span>
      </div>

      {feedbackStatus ? (
        <div className="p-2 text-center rounded bg-slate-950 border border-cyan-500/40 text-xs font-mono text-cyan-300">
          LOGGED: {feedbackStatus.toUpperCase()}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleAction('confirmed_interception')}
            className="flex items-center justify-center gap-1.5 px-2.5 py-2 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/40 text-emerald-300 rounded-lg text-xs font-semibold transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>INTERCEPTED</span>
          </button>

          <button
            onClick={() => handleAction('false_alarm')}
            className="flex items-center justify-center gap-1.5 px-2.5 py-2 bg-red-600/20 hover:bg-red-600/40 border border-red-500/40 text-red-300 rounded-lg text-xs font-semibold transition-all cursor-pointer"
          >
            <XCircle className="w-3.5 h-3.5 text-red-400" />
            <span>FALSE ALARM</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default FeedbackActions;

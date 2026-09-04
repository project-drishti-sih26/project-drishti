import React, { useState } from 'react';

/**
 * FeedbackActions Component (Role 4 - UI/UX)
 * Text-only case resolution action buttons
 */
const FeedbackActions = ({ onFeedback = () => {} }) => {
  const [feedbackSuccess, setFeedbackSuccess] = useState(null);

  const handleAction = (status) => {
    setFeedbackSuccess(status);
    onFeedback(status);
    setTimeout(() => {
      setFeedbackSuccess(null);
    }, 4000);
  };

  return (
    <div className="bg-white rounded-sm border border-slate-200 p-3.5 space-y-2.5">
      <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          Case Status Action
        </span>
        <span className="text-xs text-slate-400">Audit Trail</span>
      </div>

      {feedbackSuccess ? (
        <div className="p-2 bg-slate-100 border border-slate-300 text-slate-800 rounded-sm text-xs font-medium text-center">
          Case updated as {feedbackSuccess === 'confirmed_interception' ? 'RESOLVED' : 'UNVERIFIED'}.
        </div>
      ) : (
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => handleAction('confirmed_interception')}
            className="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-sm transition-colors cursor-pointer"
          >
            Mark Case Resolved
          </button>

          <button
            type="button"
            onClick={() => handleAction('false_alarm')}
            className="w-full py-2 px-3 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-semibold text-xs rounded-sm transition-colors cursor-pointer"
          >
            Case Unverified
          </button>
        </div>
      )}
    </div>
  );
};

export default FeedbackActions;

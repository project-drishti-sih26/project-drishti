import React from 'react';

/**
 * Header Component (Role 4 - UI/UX)
 * Plain, Bureaucratic Navigation Bar
 */
const Header = ({
  currentView = 'overview',
  onSelectView = () => {}
}) => {
  const navTabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'live_operations', label: 'Live Incident' },
    { id: 'spatial_radar', label: 'Tactical Map' },
    { id: 'analytics', label: 'Investigation Logs' }
  ];

  return (
    <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Branding */}
      <div
        onClick={() => onSelectView('overview')}
        className="flex items-center gap-2.5 cursor-pointer select-none"
      >
        <div className="w-7 h-7 rounded-sm bg-slate-900 text-white flex items-center justify-center font-bold text-xs font-mono">
          D
        </div>
        <div className="flex items-center">
          <span className="font-bold text-slate-900 text-sm tracking-tight">Drishti</span>
          <span className="text-xs text-slate-500 font-normal ml-2 border-l border-slate-200 pl-2">
            Incident Monitoring & Field Dispatch
          </span>
        </div>
      </div>

      {/* 4 Clean Feature Tabs */}
      <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-sm">
        {navTabs.map((tab) => {
          const isActive = currentView === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectView(tab.id)}
              className={`px-3 py-1 text-xs font-semibold rounded-sm transition-colors cursor-pointer ${
                isActive
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};

export default Header;

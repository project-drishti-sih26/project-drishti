import React from 'react';

/**
 * NavSidebar Component
 * Minimal, functional sidebar navigation for Project Drishti.
 * Overview is placed at the top of the navigation list.
 */
const NavSidebar = ({
  currentView = 'overview',
  onSelectView = () => {},
  hasUnreadNotification = false
}) => {
  const navItems = [
    {
      id: 'overview',
      label: 'Overview',
      hasDot: false,
      icon: (
        <svg
          className="w-4 h-4 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
        </svg>
      )
    },
    {
      id: 'cases',
      label: 'All Cases',
      hasDot: false,
      icon: (
        <svg
          className="w-4 h-4 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <line x1="7" y1="9" x2="17" y2="9" />
          <line x1="7" y1="13" x2="17" y2="13" />
          <line x1="7" y1="17" x2="12" y2="17" />
        </svg>
      )
    },
    {
      id: 'live_operations',
      label: 'Live Incidents',
      hasDot: hasUnreadNotification,
      dotColor: 'bg-rose-600',
      icon: (
        <svg
          className="w-4 h-4 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="9" />
          <circle cx="12" cy="12" r="3" />
          <line x1="12" y1="2" x2="12" y2="5" />
          <line x1="12" y1="19" x2="12" y2="22" />
          <line x1="2" y1="12" x2="5" y2="12" />
          <line x1="19" y1="12" x2="22" y2="12" />
        </svg>
      )
    },
    {
      id: 'spatial_radar',
      label: 'Map',
      hasDot: false,
      icon: (
        <svg
          className="w-4 h-4 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
          <line x1="8" y1="2" x2="8" y2="18" />
          <line x1="16" y1="6" x2="16" y2="22" />
        </svg>
      )
    }
  ];

  return (
    <aside className="w-60 bg-white border-r border-slate-200 flex flex-col shrink-0 min-h-screen select-none">
      {/* 1. BRAND HEADER */}
      <div className="h-14 px-4 border-b border-slate-200 flex items-center gap-2.5">
        <div className="w-6 h-6 flex items-center justify-center text-slate-900">
          <svg
            className="w-5 h-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.75}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
            <circle cx="12" cy="12" r="3" />
            <line x1="12" y1="3" x2="12" y2="5" />
            <line x1="12" y1="19" x2="12" y2="21" />
          </svg>
        </div>
        <span className="font-medium text-sm text-slate-900 tracking-tight">
          Drishti
        </span>
      </div>

      {/* 2. NAVIGATION LIST (Overview on top) */}
      <nav className="flex-1 p-2 space-y-0.5">
        {navItems.map((item) => {
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-[4px] text-xs transition-colors cursor-pointer ${
                isActive
                  ? 'bg-slate-100 text-slate-900 font-medium'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-normal'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className={isActive ? 'text-slate-900' : 'text-slate-500'}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </div>

              {/* Notification Dot: Displayed only if unread, removed once checked */}
              {item.hasDot && (
                <span
                  className={`w-1.5 h-1.5 rounded-full ${item.dotColor || 'bg-rose-600'}`}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* 3. RESTRAINED FOOTER */}
      <div className="p-3 border-t border-slate-200 text-xs space-y-2">
        <div className="flex items-center justify-between text-[11px] text-slate-500 font-normal">
          <span>Feed Status</span>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
            <span className="font-mono text-slate-700">1930 / I4C</span>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <span className="truncate">Insp. V. Rawat</span>
          <span className="text-[10px] font-mono text-slate-400">HQ-01</span>
        </div>
      </div>
    </aside>
  );
};

export default NavSidebar;

import React, { useState, useEffect, useRef } from 'react';

/**
 * Header Component
 * Minimal top navigation bar with clean breadcrumbs and dedicated Notification button.
 */
const Header = ({
  currentView = 'overview',
  activeCaseId = 'NCR-2026-00491',
  hasUnreadNotification = true,
  onSelectLiveIncident = () => {},
  onClearNotifications = () => {},
  onOpenDispatchModal = () => {}
}) => {
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const dropdownRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(() => {
    const now = new Date();
    return now.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' IST';
  });

  // Update live clock every second
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' IST');
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsNotificationOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getViewTitle = () => {
    switch (currentView) {
      case 'cases':
        return 'All Cases';
      case 'overview':
        return 'Overview';
      case 'live_operations':
        return `Live Incidents — ${activeCaseId}`;
      case 'spatial_radar':
      case 'map':
        return 'Map';
      default:
        return 'Dashboard';
    }
  };

  const notifications = [
    {
      id: 'notif-1',
      title: 'Urgent Fraud Incident Flagged',
      desc: 'Unauthorized transfer of ₹85,000 to HDFC •••• 9201. Proximity window: ~10m.',
      time: '2m ago',
      urgent: true
    },
    {
      id: 'notif-2',
      title: 'Patrol Unit Dispatched',
      desc: 'PCR Unit 12 en route to Connaught Place Inner Circle.',
      time: '12m ago',
      urgent: false
    },
    {
      id: 'notif-3',
      title: 'Case Resolved',
      desc: 'Case #NCR-2026-00475 funds restrained at Canara Bank Munirka.',
      time: '45m ago',
      urgent: false
    }
  ];

  return (
    <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20 select-none">
      {/* Breadcrumb: Plain & Functional */}
      <div className="flex items-center gap-2 text-xs">
        <span className="font-normal text-slate-500">Drishti</span>
        <span className="text-slate-300">/</span>
        <span className="font-medium text-slate-900">{getViewTitle()}</span>
      </div>

      {/* Right Tools: Live Clock, Section 91 Export, Notification Button */}
      <div className="flex items-center gap-3">
        {/* Live IST Clock */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] bg-slate-50 border border-slate-200 text-xs font-mono text-slate-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
          <span>{currentTime}</span>
        </div>

        {/* Export Section 91 Order Button */}
        <button
          onClick={onOpenDispatchModal}
          className="px-2.5 py-1.5 bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 text-xs font-medium rounded-[4px] transition-colors cursor-pointer flex items-center gap-1.5"
          title="Export Section 91 CrPC Police Order"
        >
          <svg className="w-3.5 h-3.5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <span>Export Section 91 Order</span>
        </button>

        {/* Dedicated Notification Button */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => {
              setIsNotificationOpen(!isNotificationOpen);
              if (hasUnreadNotification) {
                onClearNotifications();
              }
            }}
            className="w-8 h-8 rounded-[4px] border border-slate-200 bg-white hover:bg-slate-50 flex items-center justify-center text-slate-600 hover:text-slate-900 transition-colors relative cursor-pointer"
            title="Notifications"
            aria-label="View notifications"
          >
          {/* Bell Icon (Lucide style 1.75 stroke) */}
          <svg
            className="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.75}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>

          {/* Unread Indicator Dot */}
          {hasUnreadNotification && (
            <span className="w-2 h-2 rounded-full bg-rose-600 absolute top-1.5 right-1.5 ring-2 ring-white" />
          )}
        </button>

        {/* Minimal Notifications Dropdown */}
        {isNotificationOpen && (
          <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-[4px] shadow-lg py-2 z-30 space-y-1 text-xs">
            <div className="px-3.5 py-1.5 border-b border-slate-100 flex items-center justify-between">
              <span className="font-medium text-slate-900 text-xs">Notifications</span>
              <button
                onClick={() => {
                  onClearNotifications();
                  setIsNotificationOpen(false);
                }}
                className="text-xs text-slate-400 hover:text-slate-600 cursor-pointer font-normal"
              >
                Mark all read
              </button>
            </div>

            <div className="max-h-72 overflow-y-auto divide-y divide-slate-100">
              {notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => {
                    if (n.urgent) onSelectLiveIncident();
                    setIsNotificationOpen(false);
                  }}
                  className="px-3.5 py-2.5 hover:bg-slate-50 transition-colors cursor-pointer space-y-0.5"
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${n.urgent ? 'text-rose-700' : 'text-slate-900'}`}>
                      {n.title}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">{n.time}</span>
                  </div>
                  <p className="text-xs text-slate-600 font-normal leading-tight">
                    {n.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        </div>
      </div>
    </header>
  );
};

export default Header;

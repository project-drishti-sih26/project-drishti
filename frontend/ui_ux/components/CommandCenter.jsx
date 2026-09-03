import React, { useState, useEffect } from 'react';
import Header from './Header';
import Alerts from './Alerts';
import SidebarLeft from './SidebarLeft';
import CenterRadar from './CenterRadar';
import SidebarRight from './SidebarRight';
import PoliceDispatchModal from './PoliceDispatchModal';

/**
 * CommandCenter Component (Role 4 - UI/UX)
 * Cybercrime Incident Monitoring & Response Cell
 */
const CommandCenter = () => {
  const [currentView, setCurrentView] = useState('overview');
  const [isDispatchModalOpen, setIsDispatchModalOpen] = useState(false);
  const [selectedAtmId, setSelectedAtmId] = useState('ATM-091');
  const [secondsRemaining, setSecondsRemaining] = useState(656); // 10m 56s

  // Bureaucratic Active Case
  const activeCase = {
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
    assigned_patrol: 'PCR Unit 12 (Central Division)'
  };

  const [atms, setAtms] = useState([
    {
      id: 'ATM-091',
      rank: 1,
      name: 'SBI Kiosk #091',
      location: 'Block B, Inner Circle, Connaught Place',
      distance: '1.8 km',
      eta: '11 min',
      probability: '89%',
      cctv_status: 'Active (3 Cameras)',
      notes: 'Identified recurring withdrawal node for reported beneficiary syndicate.',
      xPercent: 50,
      yPercent: 46
    },
    {
      id: 'ATM-142',
      rank: 2,
      name: 'HDFC ATM',
      location: 'Statesman House, Barakhamba Road',
      distance: '2.4 km',
      eta: '17 min',
      probability: '82%',
      cctv_status: 'Active (Bank Guard)',
      notes: 'Located on transit corridor towards New Delhi Railway Station.',
      xPercent: 70,
      yPercent: 58
    },
    {
      id: 'ATM-033',
      rank: 3,
      name: 'ICICI Bank ATM',
      location: 'Janpath Market Lane',
      distance: '3.1 km',
      eta: '22 min',
      probability: '76%',
      cctv_status: 'Active (Market Feed)',
      notes: 'Pedestrian market access point.',
      xPercent: 44,
      yPercent: 74
    },
    {
      id: 'ATM-089',
      rank: 4,
      name: 'PNB ATM',
      location: 'Antriksh Bhawan, Kasturba Gandhi Marg',
      distance: '3.8 km',
      eta: '29 min',
      probability: '68%',
      cctv_status: 'Active (Building Security)',
      notes: 'Verified unoccupied during last patrol check at 22:30 IST.',
      xPercent: 76,
      yPercent: 36
    },
    {
      id: 'ATM-052',
      rank: 5,
      name: 'Axis Bank ATM',
      location: 'Outer Circle, Near Shankar Market',
      distance: '4.2 km',
      eta: '34 min',
      probability: '59%',
      cctv_status: 'Maintenance Offline',
      notes: 'Secondary node based on cell tower perimeter coverage.',
      xPercent: 58,
      yPercent: 24
    }
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCountdown = (totalSec) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSelectAtm = (atm) => {
    setSelectedAtmId(atm.id);
  };

  const handleFeedback = (actionType) => {
    if (actionType === 'intercepted') {
      setAtms(prev => prev.map(a => a.id === selectedAtmId ? { ...a, statusTag: 'Resolved' } : a));
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased">
      <Header
        currentView={currentView}
        onSelectView={setCurrentView}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-5 space-y-5">
        {currentView === 'overview' && (
          <>
            <Alerts
              alert={{
                amount: activeCase.compromised_amount,
                mule_account: activeCase.mule_account,
                countdown: formatCountdown(secondsRemaining)
              }}
              onOpenCase={() => setIsDispatchModalOpen(true)}
            />

            {/* 4 Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-3.5 rounded-sm border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block uppercase tracking-wider">Active Cases</span>
                <div className="mt-1.5 flex items-baseline justify-between">
                  <span className="text-2xl font-bold text-slate-900 font-mono">4</span>
                  <span className="text-xs text-rose-700 font-medium">2 Pending Dispatch</span>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-sm border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block uppercase tracking-wider">Total Defrauded Amount</span>
                <div className="mt-1.5 flex items-baseline justify-between">
                  <span className="text-2xl font-bold text-slate-900 font-mono">₹42.8 L</span>
                  <span className="text-xs text-slate-500">6 flagged accounts</span>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-sm border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block uppercase tracking-wider">Cases Resolved This Month</span>
                <div className="mt-1.5 flex items-baseline justify-between">
                  <span className="text-2xl font-bold text-slate-900 font-mono">18</span>
                  <span className="text-xs text-slate-700 font-medium">₹31.4L Restricted</span>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-sm border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block uppercase tracking-wider">Patrol Units on Duty</span>
                <div className="mt-1.5 flex items-baseline justify-between">
                  <span className="text-2xl font-bold text-slate-900 font-mono">8</span>
                  <span className="text-xs text-slate-600 font-medium">PCR Unit 12 Closest</span>
                </div>
              </div>
            </div>

            {/* Main Section */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-8 space-y-5">
                <SidebarLeft caseData={activeCase} />
                <CenterRadar
                  selectedAtmId={selectedAtmId}
                  onSelectAtm={handleSelectAtm}
                  atms={atms}
                />
              </div>

              <div className="lg:col-span-4">
                <SidebarRight
                  countdown={formatCountdown(secondsRemaining)}
                  selectedAtmId={selectedAtmId}
                  onSelectAtm={handleSelectAtm}
                  predictedAtms={atms}
                  onFeedback={handleFeedback}
                />
              </div>
            </div>

            {/* Analytics Section */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-8 bg-white rounded-sm border border-slate-200 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Hourly Incident Log (Delhi NCR)</h3>
                    <p className="text-xs text-slate-500">Reported volume over past 24 hours</p>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">Total Today: 24 Cases</span>
                </div>

                <div className="h-40 flex items-end justify-between gap-2 pt-4 px-2 border-b border-slate-100">
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
                    <div key={i} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                      <span className="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                        {item.count}
                      </span>
                      <div
                        className={`w-full rounded-none transition-all ${
                          item.count >= 8 ? 'bg-rose-700' : item.count >= 4 ? 'bg-slate-700' : 'bg-slate-300'
                        }`}
                        style={{ height: `${Math.max(item.count * 10, 6)}%` }}
                      />
                      <span className="text-[10px] font-mono text-slate-500 mt-1">{item.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-4 bg-white rounded-sm border border-slate-200 p-4 space-y-3">
                <div>
                  <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Fraud Category Distribution</h3>
                  <p className="text-xs text-slate-500">Breakdown of reported incident vectors</p>
                </div>

                <div className="space-y-3 pt-1">
                  {[
                    { label: 'Screen Share APK Fraud', pct: 38, count: '9 cases', color: 'bg-rose-700' },
                    { label: 'Impersonation Vishing Call', pct: 26, count: '6 cases', color: 'bg-slate-700' },
                    { label: 'KYC Phishing SMS / Link', pct: 21, count: '5 cases', color: 'bg-amber-600' },
                    { label: 'Card Cloning / Skimming', pct: 15, count: '4 cases', color: 'bg-slate-400' }
                  ].map((type, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-700">{type.label}</span>
                        <span className="text-slate-500 font-mono">{type.pct}% ({type.count})</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-100 rounded-none overflow-hidden">
                        <div className={`h-full ${type.color}`} style={{ width: `${type.pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      <PoliceDispatchModal
        isOpen={isDispatchModalOpen}
        onClose={() => setIsDispatchModalOpen(false)}
        caseDetails={{
          case_id: activeCase.case_id,
          victim_name: activeCase.victim_name,
          victim_account: activeCase.victim_account,
          mule_account: activeCase.mule_account,
          mule_name: activeCase.mule_name,
          compromised_amount: activeCase.compromised_amount,
          assigned_patrol: activeCase.assigned_patrol,
          predicted_atm: activeCase.predicted_atm,
          ranked_atms: atms.map(a => ({
            rank: a.rank,
            name: a.name,
            address: a.location,
            eta: a.eta
          }))
        }}
      />
    </div>
  );
};

export default CommandCenter;

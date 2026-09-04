import React, { useState, useEffect } from 'react';
import NavSidebar from './NavSidebar';
import Header from './Header';
import OverviewView from './OverviewView';
import AllCasesView from './AllCasesView';
import SidebarLeft from './SidebarLeft';
import CenterRadar from './CenterRadar';
import SidebarRight from './SidebarRight';
import PoliceDispatchModal from './PoliceDispatchModal';
import GisDashboard from '../../gis/components/GisDashboard.jsx';

/**
 * Initial Master Cases Registry
 */
const initialCases = [
  {
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
    assigned_patrol: 'PCR Unit 12 (Central Division)',
    status: 'Active'
  },
  {
    case_id: 'NCR-2026-00492',
    victim_name: 'Sunita Mehra',
    victim_account: 'ICIC •••• 4120',
    victim_bank: 'ICICI Bank (Defence Colony Branch)',
    mule_account: 'PUNB •••• 7731',
    mule_name: 'Rahul Verma',
    mule_bank: 'Punjab National Bank (Lajpat Nagar Branch)',
    compromised_amount: 140000,
    debit_time: '22:52 IST',
    crime_vector: 'Impersonation Vishing Call',
    predicted_atm: 'HDFC ATM, Statesman House, Barakhamba Road',
    assigned_patrol: 'PCR Unit 08 (New Delhi)',
    status: 'In Progress'
  },
  {
    case_id: 'NCR-2026-00488',
    victim_name: 'Vikram Malhotra',
    victim_account: 'HDFC •••• 6055',
    victim_bank: 'HDFC Bank (Saket Branch)',
    mule_account: 'UTIB •••• 3419',
    mule_name: 'Sunil Kumar',
    mule_bank: 'Axis Bank (Janpath Branch)',
    compromised_amount: 55000,
    debit_time: '21:30 IST',
    crime_vector: 'KYC Phishing SMS / Link',
    predicted_atm: 'ICICI Bank ATM, Janpath Market Lane',
    assigned_patrol: 'PCR Unit 04 (South Division)',
    status: 'Under Monitoring'
  },
  {
    case_id: 'NCR-2026-00482',
    victim_name: 'Anjali Sharma',
    victim_account: 'BARB •••• 8192',
    victim_bank: 'Bank of Baroda (Karol Bagh Branch)',
    mule_account: 'SBIN •••• 1044',
    mule_name: 'Deepak Yadav',
    mule_bank: 'State Bank of India (Patel Nagar Branch)',
    compromised_amount: 92000,
    debit_time: '20:15 IST',
    crime_vector: 'Unauthorized APK Screen Share',
    predicted_atm: 'PNB ATM, Antriksh Bhawan, KG Marg',
    assigned_patrol: 'PCR Unit 15 (Central)',
    status: 'Under Monitoring'
  },
  {
    case_id: 'NCR-2026-00475',
    victim_name: 'Priya Deshmukh',
    victim_account: 'SBIN •••• 3341',
    victim_bank: 'State Bank of India (Vasant Kunj Branch)',
    mule_account: 'CNRB •••• 5590',
    mule_name: 'Mohit Rawat',
    mule_bank: 'Canara Bank (Munirka Branch)',
    compromised_amount: 210000,
    debit_time: '18:20 IST',
    crime_vector: 'Impersonation Vishing Call',
    predicted_atm: 'Axis Bank ATM, Outer Circle, CP',
    assigned_patrol: 'PCR Unit 02 (South West)',
    status: 'Resolved'
  },
  {
    case_id: 'NCR-2026-00462',
    victim_name: 'Amit Verma',
    victim_account: 'KKBK •••• 9920',
    victim_bank: 'Kotak Mahindra Bank (Nehru Place Branch)',
    mule_account: 'HDFC •••• 4410',
    mule_name: 'Rajesh Gupta',
    mule_bank: 'HDFC Bank (Okhla Phase 2 Branch)',
    compromised_amount: 38000,
    debit_time: '16:45 IST',
    crime_vector: 'Card Cloning / Skimming',
    predicted_atm: 'SBI Kiosk #091, Inner Circle Block-B, CP',
    assigned_patrol: 'PCR Unit 09 (South East)',
    status: 'Resolved'
  }
];

const initialAtms = [
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
    latitude: 28.6328,
    longitude: 77.2197,
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
    latitude: 28.6295,
    longitude: 77.2274,
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
    latitude: 28.6231,
    longitude: 77.2185,
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
    latitude: 28.6255,
    longitude: 77.2241,
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
    latitude: 28.6341,
    longitude: 77.2215,
    xPercent: 58,
    yPercent: 24
  }
];

/**
 * CommandCenter Component
 * Enterprise Law Enforcement Dashboard with Left Sidebar Navigation:
 * 1) All Cases
 * 2) Overview
 * 3) Live Incidents
 * 4) Map
 */
const CommandCenter = () => {
  const [currentView, setCurrentView] = useState('overview');
  const [casesList, setCasesList] = useState(initialCases);
  const [activeCaseId, setActiveCaseId] = useState('NCR-2026-00491');
  const [selectedAtmId, setSelectedAtmId] = useState('ATM-091');
  const [atms, setAtms] = useState(initialAtms);
  const [secondsRemaining, setSecondsRemaining] = useState(656); // 10m 56s
  const [isDispatchModalOpen, setIsDispatchModalOpen] = useState(false);
  const [hasUnreadNotification, setHasUnreadNotification] = useState(true);

  const activeCase = casesList.find((c) => c.case_id === activeCaseId) || casesList[0];

  // WebSocket Integration for Live Machine Learning Feed
  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;
    let isMounted = true;

    const connectWebSocket = () => {
      try {
        const wsUrl = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000/ws/live_alerts';
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          if (isMounted) console.log(`[Drishti] Connected to WebSocket: ${wsUrl}`);
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const liveData = JSON.parse(event.data);
            if (liveData.top_5_atms && liveData.top_5_atms.length > 0) {
              const mappedAtms = liveData.top_5_atms.map((a, idx) => ({
                id: a.location_id || `ATM-${idx + 1}`,
                rank: a.rank || idx + 1,
                name: a.bank_name || 'Bank ATM',
                location: a.address || 'Address unavailable',
                distance: `${a.distance_km} km`,
                eta: `${Math.round(a.travel_time_mins)} min`,
                probability: `${Math.round((a.confidence_score || 0.85) * 100)}%`,
                cctv_status: 'Active (3 Cameras)',
                notes: a.explanation || 'Predicted high-probability withdrawal target',
                latitude: a.latitude,
                longitude: a.longitude,
                xPercent: 30 + (idx * 11),
                yPercent: 40 + ((idx % 3) * 14),
              }));
              setAtms(mappedAtms);
              setSelectedAtmId(mappedAtms[0].id);

              if (liveData.time_window && liveData.time_window.minutes_from_now) {
                setSecondsRemaining(liveData.time_window.minutes_from_now * 60);
              }

              const newLiveCase = {
                case_id: liveData.case_id || 'NCR-2026-LIVE',
                victim_name: 'Reported Victim',
                victim_account: liveData.victim_account_id || 'ACC •••• 9284',
                victim_bank: 'Interbank Transfer (IMPS/UPI)',
                mule_account: liveData.mule_account_id || 'MULE •••• X99',
                mule_name: 'Suspect Mule Runner',
                mule_bank: 'Target Beneficiary Account',
                compromised_amount: liveData.compromised_amount || 150000,
                debit_time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) + ' IST',
                crime_vector: 'High-Velocity Multi-Hop Cyber Fraud',
                predicted_atm: `${mappedAtms[0].name}, ${mappedAtms[0].location}`,
                assigned_patrol: 'PCR Unit 12 (Central Division)',
                status: 'Active'
              };

              setCasesList((prev) => [newLiveCase, ...prev.filter(c => c.case_id !== newLiveCase.case_id)]);
              setActiveCaseId(newLiveCase.case_id);
              setHasUnreadNotification(true);
            }
          } catch (e) {
            console.error('[Drishti] Error parsing alert message:', e);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          reconnectTimer = setTimeout(connectWebSocket, 4000);
        };
      } catch (err) {
        console.warn('[Drishti] WebSocket initialization warning:', err);
      }
    };

    connectWebSocket();

    return () => {
      isMounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  // Countdown timer
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

  const handleSelectView = (viewId) => {
    setCurrentView(viewId);
    if (viewId === 'live_operations') {
      setHasUnreadNotification(false);
    }
  };

  const handleSelectCase = (c) => {
    setActiveCaseId(c.case_id);
  };

  const handleOpenLiveIncident = (c) => {
    if (c) setActiveCaseId(c.case_id);
    setCurrentView('live_operations');
    setHasUnreadNotification(false);
  };

  const handleOpenMap = (c) => {
    if (c) setActiveCaseId(c.case_id);
    setCurrentView('spatial_radar');
  };

  const handleFeedback = (actionType) => {
    if (actionType === 'intercepted') {
      setCasesList(prev => prev.map(c => c.case_id === activeCaseId ? { ...c, status: 'Resolved' } : c));
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex antialiased">
      {/* 1. MINIMAL LEFT SIDEBAR NAVIGATION */}
      <NavSidebar
        currentView={currentView}
        onSelectView={handleSelectView}
        hasUnreadNotification={hasUnreadNotification}
      />

      {/* 2. MAIN APPLICATION WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <Header
          currentView={currentView}
          activeCaseId={activeCaseId}
          hasUnreadNotification={hasUnreadNotification}
          onSelectLiveIncident={() => handleSelectView('live_operations')}
          onClearNotifications={() => setHasUnreadNotification(false)}
          onOpenDispatchModal={() => setIsDispatchModalOpen(true)}
        />

        {/* Main View Area */}
        <main className="flex-1 p-5 space-y-5 max-w-7xl w-full mx-auto">
          {/* VIEW 1: ALL CASES */}
          {currentView === 'cases' && (
            <AllCasesView
              cases={casesList}
              selectedCaseId={activeCaseId}
              onSelectCase={handleSelectCase}
              onOpenLiveIncident={handleOpenLiveIncident}
              onOpenDispatchModal={() => setIsDispatchModalOpen(true)}
              onOpenMap={handleOpenMap}
            />
          )}

          {/* VIEW 2: OVERVIEW */}
          {currentView === 'overview' && (
            <OverviewView
              cases={casesList}
              onViewCase={(caseId) => {
                setActiveCaseId(caseId);
                handleSelectView('live_operations');
              }}
              onSelectView={handleSelectView}
            />
          )}

          {/* VIEW 3: LIVE INCIDENTS */}
          {currentView === 'live_operations' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                {/* Case Queue */}
                <div className="lg:col-span-4 space-y-3">
                  <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-2.5">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                      <div>
                        <h2 className="text-xs font-medium text-slate-900 uppercase">
                          Live Incidents Queue
                        </h2>
                        <p className="text-[11px] text-slate-400 font-normal">Select active incident</p>
                      </div>
                      <span className="text-xs font-mono font-normal text-slate-500">
                        {casesList.length} cases
                      </span>
                    </div>

                    <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
                      {casesList.map((c) => {
                        const isSelected = c.case_id === activeCaseId;
                        return (
                          <div
                            key={c.case_id}
                            onClick={() => setActiveCaseId(c.case_id)}
                            className={`p-2.5 rounded-[4px] border transition-colors cursor-pointer ${
                              isSelected
                                ? 'border-slate-300 bg-slate-100/90 border-l-2 border-l-slate-900'
                                : 'border-slate-200 hover:bg-slate-50 border-l-2 border-l-transparent'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-xs font-mono text-slate-900">
                                {c.case_id}
                              </span>
                              <span className={`text-[11px] font-mono leading-none px-1.5 py-0.5 rounded-[3px] border ${
                                c.status === 'Active' || c.status === 'In Progress'
                                  ? 'bg-rose-50 text-rose-700 border-rose-200'
                                  : c.status === 'Under Monitoring'
                                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                                  : 'bg-slate-100 text-slate-600 border-slate-200'
                              }`}>
                                {c.status}
                              </span>
                            </div>

                            <div className="mt-1 text-xs text-slate-800 font-normal">
                              {c.victim_name} • ₹{Number(c.compromised_amount).toLocaleString('en-IN')}
                            </div>

                            <div className="text-[11px] text-slate-400 font-normal truncate mt-0.5">
                              {c.crime_vector} • {c.debit_time}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Dossier */}
                <div className="lg:col-span-5 space-y-4">
                  <SidebarLeft caseData={activeCase} />
                </div>

                {/* Right Actions */}
                <div className="lg:col-span-3">
                  <SidebarRight
                    countdown={formatCountdown(secondsRemaining)}
                    selectedAtmId={selectedAtmId}
                    onSelectAtm={(atm) => setSelectedAtmId(atm.id)}
                    predictedAtms={atms}
                    onFeedback={handleFeedback}
                  />
                </div>
              </div>
            </div>
          )}

          {/* VIEW 4: MAP */}
          {(currentView === 'spatial_radar' || currentView === 'map') && (
            <div className="space-y-4">
              <div className="bg-white p-3.5 rounded-[4px] border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h1 className="text-xs font-medium text-slate-900 uppercase">
                    Tactical Map
                  </h1>
                  <p className="text-xs text-slate-400 font-normal mt-0.5">
                    OpenFreeMap & MapLibre Vector Engine • ATM Nodes & Patrol Routing
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-normal text-slate-500">Target Node:</span>
                  <span className="text-xs font-mono font-medium bg-slate-50 px-2 py-1 rounded-[3px] border border-slate-200">
                    {activeCase.predicted_atm}
                  </span>
                </div>
              </div>

              <div className="bg-white rounded-[4px] border border-slate-200 p-4">
                <CenterRadar
                  selectedAtmId={selectedAtmId}
                  onSelectAtm={setSelectedAtmId}
                  atms={atms}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                {atms.map((atm) => {
                  const isSelected = selectedAtmId === atm.id;
                  return (
                    <div
                      key={atm.id}
                      onClick={() => setSelectedAtmId(atm.id)}
                      className={`p-3 rounded-[4px] border transition-colors cursor-pointer bg-white ${
                        isSelected
                          ? 'border-slate-900 ring-1 ring-slate-900'
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-[3px] bg-slate-900 text-white flex items-center justify-center font-mono text-[11px] font-medium">
                            #{atm.rank}
                          </span>
                          <span className="font-medium text-xs text-slate-900">{atm.name}</span>
                        </div>
                        <span className="text-xs font-medium font-mono text-rose-700">{atm.probability}</span>
                      </div>

                      <div className="mt-1.5 text-xs text-slate-600 font-normal">{atm.location}</div>

                      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-normal">
                        <span>Distance: <strong className="text-slate-700 font-medium">{atm.distance}</strong></span>
                        <span>ETA: <strong className="text-slate-700 font-medium">{atm.eta}</strong></span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* VIEW 5: SPATIAL GIS RADAR (UBER H3) */}
          {currentView === 'gis' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between bg-white px-4 py-3 rounded-[4px] border border-slate-200">
                <div>
                  <h2 className="text-xs font-medium text-slate-900 uppercase">Spatial GIS Command Center</h2>
                  <p className="text-[11px] text-slate-400 font-normal">Live Spatio-Temporal Prediction Radar &amp; Uber H3 Hexagonal Danger Heatmap</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-[3px]">
                    Sector DL-CP (Connaught Place &amp; Delhi NCR)
                  </span>
                  <button
                    onClick={() => setCurrentView('overview')}
                    className="text-xs font-medium text-slate-600 hover:text-slate-900 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded-[3px] border border-slate-200 transition-colors cursor-pointer"
                  >
                    ← Back to Overview
                  </button>
                </div>
              </div>
              <GisDashboard />
            </div>
          )}

          {/* VIEW 6: INCIDENT LOGS & PATTERN ANALYTICS */}
          {currentView === 'analytics' && (
            <div className="space-y-4">
              <div className="bg-white p-3.5 rounded-[4px] border border-slate-200 flex items-center justify-between">
                <div>
                  <h2 className="text-xs font-medium text-slate-900 uppercase">Investigation Logs &amp; Pattern Analytics</h2>
                  <p className="text-[11px] text-slate-400 font-normal">Temporal incident velocity, syndicate withdrawal trends, and ATM cashout vectors</p>
                </div>
                <span className="text-[11px] font-mono text-slate-500">Total Logged Today: 24 Cases</span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                <div className="lg:col-span-8 bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-3">
                  <h3 className="font-medium text-slate-900 text-xs uppercase">Hourly Incident Volume (Delhi NCR)</h3>
                  <div className="h-48 flex items-end justify-between gap-2 pt-4 px-2 border-b border-slate-100">
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

                <div className="lg:col-span-4 bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-3">
                  <h3 className="font-medium text-slate-900 text-xs uppercase">Modus Operandi Distribution</h3>
                  <div className="space-y-3 pt-2">
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
            </div>
          )}
        </main>
      </div>

      {/* Police Section 91 CrPC Dispatch Order Modal */}
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
          ranked_atms: atms.map((a) => ({
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

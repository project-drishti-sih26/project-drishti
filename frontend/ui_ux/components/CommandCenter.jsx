import React, { useState, useEffect } from 'react';
import Header from './Header';
import Alerts from './Alerts';
import SidebarLeft from './SidebarLeft';
import CenterRadar from './CenterRadar';
import SidebarRight from './SidebarRight';
import PoliceDispatchModal from './PoliceDispatchModal';
import GisDashboard from '../../gis/components/GisDashboard.jsx';

/**
 * CommandCenter Component (Role 4 - UI/UX)
 * Cybercrime Incident Monitoring & Response Cell
 */
const CommandCenter = () => {
  const [currentView, setCurrentView] = useState('overview');
  const [isDispatchModalOpen, setIsDispatchModalOpen] = useState(false);
  const [selectedAtmId, setSelectedAtmId] = useState('ATM-091');
  const [secondsRemaining, setSecondsRemaining] = useState(656); // 10m 56s

  /**
   * Provenance of what is currently on screen.
   *
   * The dashboard boots with a scripted sample case so the layout is never
   * empty, and swaps to real model output the moment an alert arrives. Those
   * two states MUST be visually distinguishable: a demo figure mistaken for a
   * prediction is the single most damaging thing this UI could do, both to a
   * judge's trust and to an officer's decision.
   *
   * `degraded` mirrors the backend flag raised when the ML engine failed and a
   * database heuristic answered instead. The backend was already stamping it;
   * until now nothing rendered it, which made the flag worthless.
   */
  const [liveMeta, setLiveMeta] = useState({
    isLive: false,          // false => scripted sample data on screen
    connected: false,
    degraded: false,
    degradedReason: null,
    modelUsed: null,
    windowSource: null,
    startIst: null,
    endIst: null,
    candidatesEvaluated: null,
    top5Mass: null,
    scorecard: null,
    originLat: null,
    originLon: null,
  });

  // Dynamic Active Case State
  const [activeCase, setActiveCase] = useState({
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
    predicted_eta: '11 min',
    predicted_distance: '1.8 km',
    assigned_patrol: 'PCR Unit 12 (Central Division)'
  });

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

  // Live WebSocket Connection to Project Drishti Alert Stream
  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;
    let isMounted = true;

    const connectWebSocket = () => {
      try {
        const wsUrl = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000/ws/live_alerts';
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          if (!isMounted) return;
          console.log(`[Drishti CommandCenter] Connected to live WebSocket: ${wsUrl}`);
          setLiveMeta((m) => ({ ...m, connected: true }));
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const liveData = JSON.parse(event.data);
            console.log('[Drishti CommandCenter] Received live alert from ML Engine:', liveData);

            if (liveData.top_5_atms && liveData.top_5_atms.length > 0) {
              // 1. Update Top-5 ATMs in the Sidebar and Map
              const mappedAtms = liveData.top_5_atms.map((a, idx) => ({
                id: a.location_id || `ATM-${idx + 1}`,
                rank: a.rank || idx + 1,
                name: a.bank_name || 'Bank ATM',
                location: a.address || 'Address unavailable',
                distance: `${a.distance_km} km`,
                eta: `${Math.round(a.travel_time_mins)} min`,
                // probability_pct comes straight from the calibrated softmax.
                // The previous `(a.confidence_score || 0.85)` invented an 85%
                // whenever the field was absent OR genuinely zero — printing a
                // confident number the model never produced. If it is missing
                // now, we say so.
                probability:
                  typeof a.probability_pct === 'number'
                    ? `${a.probability_pct.toFixed(1)}%`
                    : typeof a.confidence_score === 'number'
                      ? `${(a.confidence_score * 100).toFixed(1)}%`
                      : 'n/a',
                risk_tier: a.risk_tier || null,
                // CCTV coverage is not in any dataset we hold. It used to be
                // hardcoded to "Active (3 Cameras)" for every live ATM, which
                // is fabricated evidence on a dispatch screen.
                cctv_status: 'Not integrated (no CCTV feed)',
                notes: a.explanation || 'Predicted high-probability withdrawal target',
                latitude: a.latitude,
                longitude: a.longitude,
                xPercent: 30 + (idx * 11),
                yPercent: 40 + ((idx % 3) * 14),
              }));
              setAtms(mappedAtms);
              setSelectedAtmId(mappedAtms[0].id);

              // 2. Update Countdown Timer from Survival Analysis prediction.
              //    `&& liveData.time_window.minutes_from_now` was falsy at 0 —
              //    exactly the case where the interception window is ALREADY
              //    OPEN, i.e. the most urgent alert the system can raise. It
              //    kept the stale 10:56 demo countdown on screen instead.
              const tw = liveData.time_window;
              const lead = tw && typeof tw === 'object' ? tw.minutes_from_now : null;
              if (typeof lead === 'number' && Number.isFinite(lead)) {
                setSecondsRemaining(Math.max(0, Math.round(lead * 60)));
              }

              setLiveMeta({
                isLive: true,
                connected: true,
                degraded: liveData.degraded === true,
                degradedReason: liveData.degraded_reason || null,
                modelUsed: liveData.model_used || null,
                windowSource: tw && typeof tw === 'object' ? tw.model_source : null,
                startIst: tw && typeof tw === 'object' ? tw.start_ist : null,
                endIst: tw && typeof tw === 'object' ? tw.end_ist : null,
                candidatesEvaluated: liveData.total_candidates_evaluated ?? null,
                top5Mass: liveData.top5_probability_mass ?? null,
                scorecard: liveData.model_scorecard || null,
                originLat: liveData.mule_location_known ? liveData.mule_last_latitude : null,
                originLon: liveData.mule_location_known ? liveData.mule_last_longitude : null,
              });

              // 3. Update the Active Incident Case Details
              setActiveCase({
                case_id: liveData.case_id || 'NCR-2026-LIVE',
                victim_name: 'Reported Victim',
                victim_account: liveData.victim_account_id || 'ACC •••• 9284',
                victim_bank: 'Interbank Transfer (IMPS/UPI)',
                mule_account: liveData.mule_account_id || 'MULE •••• X99',
                mule_name: 'Suspect Mule Runner',
                mule_bank: 'Target Beneficiary Account',
                compromised_amount: liveData.compromised_amount || 150000,
                debit_time: liveData.detected_at_ist
                  || new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) + ' IST',
                crime_vector: 'High-Velocity Multi-Hop Cyber Fraud',
                predicted_atm: `${mappedAtms[0].name}, ${mappedAtms[0].location}`,
                predicted_eta: mappedAtms[0].eta,
                predicted_distance: mappedAtms[0].distance,
                assigned_patrol: 'PCR Unit 12 (Central Division)'
              });
            }
          } catch (e) {
            console.error('[Drishti CommandCenter] Failed to parse alert message:', e);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setLiveMeta((m) => ({ ...m, connected: false }));
          reconnectTimer = setTimeout(connectWebSocket, 4000);
        };
      } catch (err) {
        console.warn('[Drishti CommandCenter] WebSocket connection error:', err);
      }
    };

    connectWebSocket();

    return () => {
      isMounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

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

      {/*
        PROVENANCE STRIP — always on screen, in every view.

        Answers three questions a judge or a duty officer will ask, without
        anyone having to open a console:
          1. Is this a real model prediction, or the scripted sample?
          2. Which model produced it, and how accurate is that model?
          3. Did the ML engine fail and quietly hand over to a heuristic?
        (3) is the important one. The backend stamps `degraded` when inference
        raised and a database heuristic answered instead. An unrendered flag
        protects nobody, so a failure now takes over the top of the screen.
      */}
      {liveMeta.degraded ? (
        <div className="bg-rose-700 text-white px-5 py-2.5 border-b-2 border-rose-900">
          <div className="max-w-7xl mx-auto flex items-start gap-3">
            <span className="font-bold text-xs uppercase tracking-widest shrink-0 pt-px">
              ⚠ Degraded
            </span>
            <span className="text-xs leading-relaxed">
              {liveMeta.degradedReason
                || 'ML engine unavailable — this is a database heuristic, NOT a model prediction.'}
              {' '}Do not dispatch on these rankings.
            </span>
          </div>
        </div>
      ) : (
        <div className={`px-5 py-2 border-b text-[11px] ${liveMeta.isLive
          ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
          : 'bg-amber-50 border-amber-200 text-amber-900'}`}>
          <div className="max-w-7xl mx-auto flex flex-wrap items-center gap-x-5 gap-y-1">
            <span className="font-bold uppercase tracking-widest">
              {liveMeta.isLive ? '● Live prediction' : '○ Sample case (awaiting live alert)'}
            </span>

            {liveMeta.isLive && (
              <>
                <span className="font-mono">
                  Ranker: <strong>{liveMeta.modelUsed || 'unknown'}</strong>
                </span>
                <span className="font-mono">
                  Window: <strong>{liveMeta.windowSource || 'unknown'}</strong>
                </span>
                {liveMeta.startIst && liveMeta.endIst && (
                  <span className="font-mono">
                    Intercept <strong>{liveMeta.startIst}–{liveMeta.endIst} IST</strong>
                  </span>
                )}
                {liveMeta.candidatesEvaluated != null && (
                  <span className="font-mono">
                    {liveMeta.candidatesEvaluated} cash points searched
                  </span>
                )}
                {typeof liveMeta.top5Mass === 'number' && (
                  <span className="font-mono">
                    Top-5 holds {(liveMeta.top5Mass * 100).toFixed(0)}% of probability
                  </span>
                )}
                {liveMeta.scorecard?.top5_hit_rate && (
                  <span className="font-mono">
                    Held-out accuracy: Top-1 <strong>{(liveMeta.scorecard.top1_hit_rate * 100).toFixed(1)}%</strong>,
                    Top-5 <strong>{(liveMeta.scorecard.top5_hit_rate * 100).toFixed(1)}%</strong>
                    {liveMeta.scorecard.evaluated_on_queries
                      ? ` (n=${liveMeta.scorecard.evaluated_on_queries} unseen cases)`
                      : ''}
                  </span>
                )}
              </>
            )}

            <span className={`ml-auto font-mono ${liveMeta.connected ? 'text-slate-500' : 'text-rose-700 font-bold'}`}>
              {liveMeta.connected ? 'WS connected' : 'WS disconnected — reconnecting…'}
            </span>
          </div>
        </div>
      )}

      <main className="flex-1 max-w-7xl w-full mx-auto p-5 space-y-5">
        {currentView === 'overview' && (
          <>
            <Alerts
              alert={{
                amount: activeCase.compromised_amount,
                mule_account: activeCase.mule_account,
                countdown: formatCountdown(secondsRemaining),
                startIst: liveMeta.startIst,
                endIst: liveMeta.endIst,
                detectedAtIst: liveMeta.isLive ? activeCase.debit_time : null,
              }}
              onOpenCase={() => setIsDispatchModalOpen(true)}
            />

            {/* 4 Metric Cards — illustrative cell-level statistics, not model
                output. Labelled so nobody reads them as measured results. */}
            <div className="flex items-center justify-between">
              <h3 className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Cell Statistics</h3>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">Illustrative — not model output</span>
            </div>
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
                  originLat={liveMeta.originLat}
                  originLon={liveMeta.originLon}
                  atms={atms}
                />
              </div>

              <div className="lg:col-span-4">
                <SidebarRight
                  countdown={formatCountdown(secondsRemaining)}
                  windowIst={liveMeta.startIst && liveMeta.endIst
                    ? `${liveMeta.startIst}–${liveMeta.endIst} IST` : null}
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

        {currentView === 'spatial_radar' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-white px-4 py-3 rounded-sm border border-slate-200">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Tactical Spatial GIS Command Center</h2>
                <p className="text-xs text-slate-500">Live Spatio-Temporal Prediction Radar & Uber H3 Hexagonal Danger Heatmap</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-sm">
                  Sector DL-CP (Connaught Place & Delhi NCR)
                </span>
                <button
                  onClick={() => setCurrentView('overview')}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-sm border border-slate-300 transition-colors"
                >
                  ← Back to Overview
                </button>
              </div>
            </div>
            <GisDashboard />
          </div>
        )}

        {currentView === 'live_operations' && (
          <div className="space-y-5">
            <Alerts
              alert={{
                amount: activeCase.compromised_amount,
                mule_account: activeCase.mule_account,
                countdown: formatCountdown(secondsRemaining),
                startIst: liveMeta.startIst,
                endIst: liveMeta.endIst,
                detectedAtIst: liveMeta.isLive ? activeCase.debit_time : null,
              }}
              onOpenCase={() => setIsDispatchModalOpen(true)}
            />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-8 space-y-5">
                <SidebarLeft caseData={activeCase} />
                <CenterRadar
                  selectedAtmId={selectedAtmId}
                  onSelectAtm={handleSelectAtm}
                  originLat={liveMeta.originLat}
                  originLon={liveMeta.originLon}
                  atms={atms}
                />
              </div>
              <div className="lg:col-span-4">
                <SidebarRight
                  countdown={formatCountdown(secondsRemaining)}
                  windowIst={liveMeta.startIst && liveMeta.endIst
                    ? `${liveMeta.startIst}–${liveMeta.endIst} IST` : null}
                  selectedAtmId={selectedAtmId}
                  onSelectAtm={handleSelectAtm}
                  predictedAtms={atms}
                  onFeedback={handleFeedback}
                />
              </div>
            </div>
          </div>
        )}

        {currentView === 'analytics' && (
          <div className="space-y-5">
            <div className="bg-white p-4 rounded-sm border border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Investigation Logs & Pattern Analytics</h2>
                <p className="text-xs text-slate-500">Temporal incident velocity, syndicate withdrawal trends, and ATM cashout vectors</p>
              </div>
              <span className="text-xs font-mono text-slate-500">Total Logged Today: 24 Cases</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-8 bg-white rounded-sm border border-slate-200 p-4 space-y-3">
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Hourly Incident Volume (Delhi NCR)</h3>
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

              <div className="lg:col-span-4 bg-white rounded-sm border border-slate-200 p-4 space-y-3">
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Modus Operandi Distribution</h3>
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

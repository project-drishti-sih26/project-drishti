import React, { useState } from 'react';
import MapRadar from '../../gis/components/MapRadar.jsx';

/**
 * CenterRadar Component
 * Live Location Map — Delhi NCR with interactive MapLibre vector map and hex grid view toggle.
 */
const CenterRadar = ({
  selectedAtmId = 'ATM-091',
  onSelectAtm = () => {},
  atms = [
    {
      id: 'ATM-091',
      rank: 1,
      name: 'SBI Kiosk #091',
      location: 'Block B, Inner Circle, Connaught Place',
      distance: '1.8 km',
      eta: '11 min',
      probability: '89%',
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
      xPercent: 58,
      yPercent: 24
    }
  ]
}) => {
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'schematic'

  return (
    <div className="bg-white rounded-[4px] border border-slate-200 p-4 flex flex-col space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium text-slate-900 text-xs">
            Live Location Map — Delhi NCR
          </h3>
          <p className="text-xs text-slate-500 font-normal">
            GPS: 28.6328° N, 77.2195° E • Central Division
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode(viewMode === 'map' ? 'schematic' : 'map')}
            className="text-[11px] font-normal px-2.5 py-1 rounded-[3px] bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors cursor-pointer"
          >
            {viewMode === 'map' ? 'Show Hex Grid View' : 'Show Map View'}
          </button>
          <span className="text-[11px] font-mono font-medium px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-[3px]">
            PCR 12 En Route
          </span>
        </div>
      </div>

      {/* Map Container */}
      <div className="w-full min-h-[450px] flex-1 bg-slate-900 rounded-[4px] relative overflow-hidden border border-slate-800 select-none">
        {viewMode === 'map' ? (
          <div className="w-full h-[450px]">
            <MapRadar
              locations={atms.map((a, i) => ({
                id: a.id,
                rank: a.rank || i + 1,
                bank_name: a.name,
                address: a.location || a.address,
                latitude: a.latitude || (28.6315 + ((a.yPercent || 50) - 50) * 0.0008),
                longitude: a.longitude || (77.2167 + ((a.xPercent || 50) - 50) * 0.0008),
                distance_km: parseFloat(a.distance) || 1.8,
                travel_time_mins: parseFloat(a.eta) || 11,
                riskScore: (parseFloat(a.probability) || 85) / 100
              }))}
              selectedLocationId={selectedAtmId}
              onSelectLocation={(loc) => onSelectAtm(loc.id)}
              showTargetsPanel={false}
              showLegend={false}
            />
          </div>
        ) : (
          <>
            <svg className="absolute inset-0 w-full h-full opacity-60">
              <circle cx="50%" cy="50%" r="50" fill="none" stroke="#334155" strokeWidth="1.5" />
              <circle cx="50%" cy="50%" r="110" fill="none" stroke="#334155" strokeWidth="1.5" strokeDasharray="6 6" />
              <circle cx="50%" cy="50%" r="170" fill="none" stroke="#1e293b" strokeWidth="1.5" />

              <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#334155" strokeWidth="1" />
              <line x1="0" y1="50%" x2="100%" y2="50%" stroke="#334155" strokeWidth="1" />
              <line x1="20%" y1="20%" x2="80%" y2="80%" stroke="#1e293b" strokeWidth="1" />
              <line x1="80%" y1="20%" x2="20%" y2="80%" stroke="#1e293b" strokeWidth="1" />

              <line x1="30%" y1="36%" x2="50%" y2="46%" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="4 4" />
            </svg>

            <span className="absolute text-[10px] text-slate-500 font-mono" style={{ left: '52%', top: '51%' }}>
              CP Central Park
            </span>
            <span className="absolute text-[9px] text-slate-600 font-mono" style={{ left: '72%', top: '65%' }}>
              Barakhamba Rd
            </span>
            <span className="absolute text-[9px] text-slate-600 font-mono" style={{ left: '38%', top: '78%' }}>
              Janpath Lane
            </span>

            {/* Patrol Car Marker */}
            <div
              className="absolute z-20 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
              style={{ left: '30%', top: '36%' }}
            >
              <div className="w-5 h-5 rounded-[3px] bg-slate-700 text-white flex items-center justify-center font-mono font-medium text-[10px] border border-slate-500">
                P12
              </div>
              <span className="text-[10px] font-mono text-slate-200 bg-slate-800 px-1.5 py-0.5 rounded-[3px] border border-slate-700 mt-1">
                PCR-12 (1.4 km)
              </span>
            </div>

            {/* Flat Hard-Edged ATM Markers */}
            {atms.map((atm) => {
              const isSelected = selectedAtmId === atm.id;
              return (
                <div
                  key={atm.id}
                  onClick={() => onSelectAtm(atm)}
                  className="absolute z-20 -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                  style={{ left: `${atm.xPercent}%`, top: `${atm.yPercent}%` }}
                >
                  <div className="flex flex-col items-center">
                    <div className={`w-5 h-5 rounded-[3px] flex items-center justify-center font-mono font-medium text-[10px] ${
                      atm.rank === 1
                        ? 'bg-rose-700 text-white border border-rose-900'
                        : atm.rank <= 3
                        ? 'bg-amber-600 text-white border border-amber-800'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    } ${isSelected ? 'ring-2 ring-slate-400' : ''}`}>
                      #{atm.rank}
                    </div>
                    <span className="bg-slate-800 text-slate-300 text-[10px] font-mono px-1 py-0.5 rounded-[3px] border border-slate-700 mt-1 whitespace-nowrap">
                      {atm.name}
                    </span>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};

export default CenterRadar;

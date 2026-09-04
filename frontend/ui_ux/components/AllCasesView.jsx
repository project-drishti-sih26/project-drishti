import React, { useState } from 'react';

/**
 * AllCasesView Component
 * Master Case Register for Project Drishti
 * Clean, data-dense enterprise table with sortable columns, high-contrast labels, and consistent account format.
 */
const AllCasesView = ({
  cases = [],
  selectedCaseId = 'NCR-2026-00491',
  onSelectCase = () => {},
  onOpenLiveIncident = () => {},
  onOpenDispatchModal = () => {},
  onOpenMap = () => {}
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortField, setSortField] = useState(null); // null (default timestamp order) | 'amount' | 'status'
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc' | 'desc'

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.victim_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.victim_account.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.victim_bank.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.mule_account.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.mule_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.mule_bank.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.crime_vector.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.predicted_atm.toLowerCase().includes(searchQuery.toLowerCase());

    if (statusFilter === 'ALL') return matchesSearch;
    if (statusFilter === 'ACTIVE') return matchesSearch && (c.status === 'Active' || c.status === 'In Progress');
    if (statusFilter === 'MONITORING') return matchesSearch && c.status === 'Under Monitoring';
    if (statusFilter === 'RESOLVED') return matchesSearch && (c.status === 'Resolved' || c.status === 'Restricted');
    return matchesSearch;
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection(field === 'amount' ? 'desc' : 'asc');
    }
  };

  const sortedAndFilteredCases = [...filteredCases].sort((a, b) => {
    if (!sortField) return 0; // Default most-recent-first order

    if (sortField === 'amount') {
      const amtA = Number(a.compromised_amount) || 0;
      const amtB = Number(b.compromised_amount) || 0;
      return sortDirection === 'asc' ? amtA - amtB : amtB - amtA;
    }

    if (sortField === 'status') {
      const statusA = a.status || '';
      const statusB = b.status || '';
      return sortDirection === 'asc'
        ? statusA.localeCompare(statusB)
        : statusB.localeCompare(statusA);
    }

    return 0;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Active':
      case 'In Progress':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'Under Monitoring':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Resolved':
      case 'Restricted':
        return 'bg-slate-100 text-slate-600 border-slate-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const activeSelectedCase = cases.find((c) => c.case_id === selectedCaseId) || cases[0];

  return (
    <div className="space-y-4">
      {/* Header & Unified Summary Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-[4px] border border-slate-200">
        <div>
          <h1 className="text-sm font-medium text-slate-900">
            All Cases
          </h1>
          <p className="text-xs text-slate-500 font-normal mt-0.5">
            1930 / I4C Portal Registry
          </p>
        </div>

        {/* Unified 3-Stat Summary Panel */}
        <div className="flex items-center bg-slate-50/70 rounded-[4px] border border-slate-200 divide-x divide-slate-200 overflow-hidden shadow-2xs">
          {/* Stat 1: Total */}
          <div className="w-24 px-3 py-1.5 text-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium block">
              Total
            </span>
            <span className="text-base font-semibold text-slate-900 font-mono leading-tight mt-0.5 block">
              {cases.length}
            </span>
          </div>

          {/* Stat 2: Urgent (Red value only, no background tint) */}
          <div className="w-24 px-3 py-1.5 text-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium block">
              Urgent
            </span>
            <span className="text-base font-semibold text-rose-700 font-mono leading-tight mt-0.5 block">
              {cases.filter((c) => c.status === 'Active' || c.status === 'In Progress').length}
            </span>
          </div>

          {/* Stat 3: Restrained */}
          <div className="w-24 px-3 py-1.5 text-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium block">
              Restrained
            </span>
            <span className="text-base font-semibold text-slate-900 font-mono leading-tight mt-0.5 block">
              ₹31.4 L
            </span>
          </div>
        </div>
      </div>

      {/* 1. FILTER TAB EMPHASIS & SEARCH */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-1 bg-white p-1 rounded-[4px] border border-slate-200 w-full sm:w-auto">
          {[
            { id: 'ALL', label: 'All Cases', count: cases.length },
            { id: 'ACTIVE', label: 'Urgent', count: cases.filter(c => c.status === 'Active' || c.status === 'In Progress').length },
            { id: 'MONITORING', label: 'Under Monitoring', count: cases.filter(c => c.status === 'Under Monitoring').length },
            { id: 'RESOLVED', label: 'Resolved', count: cases.filter(c => c.status === 'Resolved' || c.status === 'Restricted').length }
          ].map((tab) => {
            const isActive = statusFilter === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1 text-xs rounded-[3px] transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-slate-900 text-white font-medium shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-normal'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            );
          })}
        </div>

        <div className="w-full sm:w-72 relative">
          <input
            type="text"
            placeholder="Search cases, accounts, banks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-[4px] text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-400 font-normal"
          />
          <svg
            className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.75}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Grid: Case List + Inspection Dossier */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Cases Table */}
        <div className="lg:col-span-8 bg-white rounded-[4px] border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-normal text-xs">
                <tr>
                  <th className="py-2.5 px-3">Case ID</th>
                  <th className="py-2.5 px-3">Victim Account</th>
                  <th className="py-2.5 px-3">Mule Account</th>
                  
                  {/* 4. SORTABLE COLUMN: AMOUNT */}
                  <th
                    className="py-2.5 px-3 text-right cursor-pointer select-none group hover:text-slate-900"
                    onClick={() => handleSort('amount')}
                  >
                    <div className="inline-flex items-center gap-1">
                      <span>Amount</span>
                      <span className="font-mono text-xs text-slate-400 group-hover:text-slate-700">
                        {sortField === 'amount' ? (sortDirection === 'asc' ? '▲' : '▼') : '⇅'}
                      </span>
                    </div>
                  </th>

                  {/* 4. SORTABLE COLUMN: STATUS */}
                  <th
                    className="py-2.5 px-3 cursor-pointer select-none group hover:text-slate-900"
                    onClick={() => handleSort('status')}
                  >
                    <div className="inline-flex items-center gap-1">
                      <span>Status</span>
                      <span className="font-mono text-xs text-slate-400 group-hover:text-slate-700">
                        {sortField === 'status' ? (sortDirection === 'asc' ? '▲' : '▼') : '⇅'}
                      </span>
                    </div>
                  </th>

                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal">
                {sortedAndFilteredCases.map((c) => {
                  const isSelected = c.case_id === selectedCaseId;
                  return (
                    <tr
                      key={c.case_id}
                      onClick={() => onSelectCase(c)}
                      className={`transition-colors cursor-pointer ${
                        isSelected ? 'bg-slate-50/90' : 'hover:bg-slate-50'
                      }`}
                    >
                      {/* Case ID / Time with left selection indicator */}
                      <td className={`py-2.5 px-3 border-l-2 transition-colors ${
                        isSelected ? 'border-l-slate-900 bg-slate-50' : 'border-l-transparent'
                      }`}>
                        <div className="font-medium text-slate-900 font-mono">{c.case_id}</div>
                        <div className="text-xs text-slate-500 font-normal">{c.debit_time}</div>
                      </td>

                      {/* 3. STANDARDIZED VICTIM ACCOUNT DISPLAY */}
                      <td className="py-2.5 px-3">
                        <div className="font-medium text-slate-900">{c.victim_name}</div>
                        <div className="text-xs text-slate-700 font-mono font-medium">{c.victim_account}</div>
                        <div className="text-xs text-slate-500 font-normal">{c.victim_bank}</div>
                      </td>

                      {/* 3. STANDARDIZED MULE ACCOUNT DISPLAY */}
                      <td className="py-2.5 px-3">
                        <div className="font-medium text-slate-900">{c.mule_name}</div>
                        <div className="text-xs text-slate-700 font-mono font-medium">{c.mule_account}</div>
                        <div className="text-xs text-slate-500 font-normal">{c.mule_bank}</div>
                      </td>

                      {/* Amount */}
                      <td className="py-2.5 px-3 text-right">
                        <div className="font-medium text-slate-900 font-mono">
                          ₹{Number(c.compromised_amount).toLocaleString('en-IN')}
                        </div>
                        <div className="text-xs text-slate-500 font-normal">{c.crime_vector}</div>
                      </td>

                      {/* Status */}
                      <td className="py-2.5 px-3">
                        <span className={`inline-block text-xs font-mono leading-none px-1.5 py-0.5 rounded-[3px] border ${getStatusBadge(c.status)}`}>
                          {c.status}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-2.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => {
                            onSelectCase(c);
                            onOpenLiveIncident(c);
                          }}
                          className="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {sortedAndFilteredCases.length === 0 && (
            <div className="p-8 text-center text-slate-500 text-xs font-normal">
              No cases match the query.
            </div>
          )}
        </div>

        {/* Selected Case Dossier */}
        {activeSelectedCase && (
          <div className="lg:col-span-4 bg-white rounded-[4px] border border-slate-200 p-4 space-y-3">
            <div className="pb-2.5 border-b border-slate-100 flex items-center justify-between">
              <div>
                {/* 2. DARKENED LABEL CONTRAST */}
                <span className="text-xs font-medium text-slate-700 uppercase tracking-wide block">
                  Case Details
                </span>
                <div className="text-xs font-medium text-slate-900 font-mono">
                  {activeSelectedCase.case_id}
                </div>
              </div>
              <span className={`text-xs font-mono leading-none px-1.5 py-0.5 rounded-[3px] border ${getStatusBadge(activeSelectedCase.status)}`}>
                {activeSelectedCase.status}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              {/* Reported Amount */}
              <div className="p-2.5 bg-slate-50 rounded-[3px] border border-slate-200">
                {/* 2. DARKENED LABEL CONTRAST */}
                <span className="text-xs font-medium text-slate-700 uppercase tracking-wide block">
                  Reported Amount
                </span>
                <span className="text-base font-medium font-mono text-slate-900">
                  ₹{Number(activeSelectedCase.compromised_amount).toLocaleString('en-IN')}
                </span>
                <div className="text-xs text-slate-600 font-normal mt-0.5">
                  Logged: {activeSelectedCase.debit_time} • {activeSelectedCase.crime_vector}
                </div>
              </div>

              {/* 3. STANDARDIZED VICTIM ACCOUNT IN DETAILS PANEL */}
              <div className="space-y-1">
                {/* 2. DARKENED LABEL CONTRAST */}
                <span className="text-xs font-medium text-slate-700 uppercase tracking-wide block">
                  Victim Account
                </span>
                <div className="p-2 bg-slate-50/70 rounded-[3px] border border-slate-200 space-y-0.5">
                  <div className="font-medium text-slate-900">{activeSelectedCase.victim_name}</div>
                  <div className="text-slate-800 font-mono text-xs font-medium">{activeSelectedCase.victim_account}</div>
                  <div className="text-slate-600 text-xs font-normal">{activeSelectedCase.victim_bank}</div>
                </div>
              </div>

              {/* 3. STANDARDIZED MULE ACCOUNT IN DETAILS PANEL */}
              <div className="space-y-1">
                {/* 2. DARKENED LABEL CONTRAST */}
                <span className="text-xs font-medium text-slate-700 uppercase tracking-wide block">
                  Mule Account
                </span>
                <div className="p-2 bg-slate-50/70 rounded-[3px] border border-slate-200 space-y-0.5">
                  <div className="font-medium text-slate-900">{activeSelectedCase.mule_name}</div>
                  <div className="text-slate-800 font-mono text-xs font-medium">{activeSelectedCase.mule_account}</div>
                  <div className="text-slate-600 text-xs font-normal">{activeSelectedCase.mule_bank}</div>
                </div>
              </div>

              {/* Predicted ATM Node */}
              <div className="space-y-1">
                {/* 2. DARKENED LABEL CONTRAST */}
                <span className="text-xs font-medium text-slate-700 uppercase tracking-wide block">
                  Predicted ATM Node
                </span>
                <div className="p-2 bg-slate-50/70 rounded-[3px] border border-slate-200 space-y-0.5">
                  <div className="font-medium text-slate-900">{activeSelectedCase.predicted_atm}</div>
                  <div className="text-slate-600 text-xs font-normal">Assigned: {activeSelectedCase.assigned_patrol}</div>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 space-y-1.5">
              <button
                onClick={() => onOpenLiveIncident(activeSelectedCase)}
                className="w-full py-1.5 px-3 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
              >
                Open in Live Incidents
              </button>
              <button
                onClick={() => onOpenDispatchModal(activeSelectedCase)}
                className="w-full py-1.5 px-3 bg-white hover:bg-slate-50 text-slate-900 border border-slate-200 font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
              >
                Export Section 91 Order
              </button>
              <button
                onClick={() => onOpenMap(activeSelectedCase)}
                className="w-full py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
              >
                View on Map
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AllCasesView;

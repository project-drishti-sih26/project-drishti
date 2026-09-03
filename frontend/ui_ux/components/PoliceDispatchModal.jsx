import React from 'react';
import { jsPDF } from 'jspdf';

/**
 * PoliceDispatchModal Component (Role 4 - UI/UX)
 * Police Dispatch Order Preview & PDF Export
 */
const PoliceDispatchModal = ({
  isOpen = false,
  onClose = () => {},
  caseDetails = {
    case_id: 'NCR-2026-00491',
    victim_name: 'R. K. Sharma',
    victim_account: 'SBIN •••• 9284',
    mule_account: 'HDFC •••• 9201',
    mule_name: 'Imran Ansari',
    compromised_amount: 85000,
    assigned_patrol: 'PCR Unit 12 (Central Division)',
    predicted_atm: 'SBI Kiosk #091, Inner Circle Block-B, CP',
    ranked_atms: [
      { rank: 1, name: 'SBI Kiosk #091', address: 'Block B, Inner Circle, Connaught Place', eta: '11 min' },
      { rank: 2, name: 'HDFC ATM', address: 'Statesman House, Barakhamba Road', eta: '17 min' },
      { rank: 3, name: 'ICICI Bank ATM', address: 'Janpath Market Lane', eta: '22 min' },
      { rank: 4, name: 'PNB ATM', address: 'Antriksh Bhawan, KG Marg', eta: '29 min' },
      { rank: 5, name: 'Axis Bank ATM', address: 'Outer Circle, Near Shankar Market', eta: '34 min' }
    ]
  }
}) => {
  if (!isOpen) return null;

  const generatePDF = () => {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    doc.setFillColor(15, 23, 42);
    doc.rect(10, 10, 190, 22, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.text('DELHI POLICE CYBER CRIME CELL // POLICE DISPATCH ORDER', 14, 18);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(203, 213, 225);
    doc.text('Issued under Section 91 CrPC for Physical ATM Verification & Interception', 14, 26);

    doc.setTextColor(15, 23, 42);
    doc.setFontSize(10);
    doc.text(`Case File Reference: ${caseDetails.case_id}`, 14, 42);
    doc.text(`Reported Loss Amount: INR ${Number(caseDetails.compromised_amount).toLocaleString('en-IN')}`, 14, 49);
    doc.text(`Victim: ${caseDetails.victim_name} (${caseDetails.victim_account})`, 14, 56);
    doc.text(`Beneficiary Mule Account: ${caseDetails.mule_account} [${caseDetails.mule_name}]`, 14, 63);
    doc.text(`Assigned Patrol Unit: ${caseDetails.assigned_patrol || 'PCR Unit 12'}`, 14, 70);
    doc.text(`Predicted Withdrawal Location: ${caseDetails.predicted_atm}`, 14, 77);

    doc.setDrawColor(226, 232, 240);
    doc.line(14, 84, 196, 84);

    doc.setFont('helvetica', 'bold');
    doc.text('Ranked ATM Locations in Target Sector:', 14, 94);
    doc.setFont('helvetica', 'normal');
    (caseDetails.ranked_atms || []).forEach((atm, i) => {
      doc.text(`#${atm.rank} - ${atm.name} | ${atm.address} | ETA: ${atm.eta}`, 14, 104 + (i * 8));
    });

    doc.save(`Dispatch_${caseDetails.case_id}.pdf`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-none p-4">
      <div className="bg-white rounded-sm max-w-lg w-full shadow-lg border border-slate-300 overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Police Dispatch Order</h3>
            <p className="text-xs text-slate-500">Notice under Section 91 CrPC</p>
          </div>
          <button
            onClick={onClose}
            className="px-2 py-1 text-xs font-mono text-slate-500 hover:text-slate-900 cursor-pointer"
          >
            [Close]
          </button>
        </div>

        <div className="p-4 space-y-3 text-xs">
          <div className="bg-slate-50 p-3 rounded-sm border border-slate-200 space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Case Reference:</span>
              <span className="font-mono font-bold text-slate-900">{caseDetails.case_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Reported Loss Amount:</span>
              <span className="font-mono font-bold text-rose-800">₹{Number(caseDetails.compromised_amount).toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Beneficiary Mule Account:</span>
              <span className="font-mono font-semibold text-slate-800">{caseDetails.mule_account} ({caseDetails.mule_name})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Assigned Patrol Unit:</span>
              <span className="font-semibold text-slate-800">{caseDetails.assigned_patrol || 'PCR Unit 12'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Predicted Withdrawal Location:</span>
              <span className="font-semibold text-slate-900">{caseDetails.predicted_atm}</span>
            </div>
          </div>

          <p className="text-slate-500 text-[11px] leading-relaxed">
            This official notice directs quick-response field units to verify ongoing cash withdrawals at the identified physical ATM location.
          </p>
        </div>

        <div className="p-3 bg-slate-50 border-t border-slate-200 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-200 rounded-sm cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={generatePDF}
            className="px-3 py-1.5 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white rounded-sm cursor-pointer"
          >
            Download PDF Order
          </button>
        </div>
      </div>
    </div>
  );
};

export default PoliceDispatchModal;

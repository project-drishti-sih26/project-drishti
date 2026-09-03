import React from 'react';
import { jsPDF } from 'jspdf';
import { FileDown, X, Shield, Printer, Check } from 'lucide-react';

/**
 * PoliceDispatchModal Component (Role 4 - UI/UX)
 * Killer Feature 1: Generates an official, formatted Police Dispatch PDF with case details,
 * suspected mule info, top-ranked ATM coordinates, and dispatch stamp for field units.
 */
const PoliceDispatchModal = ({
  isOpen = false,
  onClose = () => {},
  caseDetails = {
    case_id: 'CYB-2026-00491',
    mule_account: 'HDFC-8839201',
    compromised_amount: 85000,
    time_window: '25 - 40 Mins',
    top_atm: 'SBI ATM, Connaught Place, Block B',
    dispatch_unit: 'PCR Unit 12 - New Delhi District'
  }
}) => {
  if (!isOpen) return null;

  const generatePDF = () => {
    const doc = new jsPDF();

    // Official Header Banner
    doc.setFillColor(15, 23, 42); // Dark slate
    doc.rect(0, 0, 210, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('PROJECT DRISHTI - EMERGENCY DISPATCH ORDER', 14, 18);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(56, 189, 248); // Cyan
    doc.text('INDIAN CYBERCRIME COORDINATION CENTRE (I4C) | MINISTRY OF HOME AFFAIRS', 14, 26);

    // Metadata
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(11);
    doc.text(`Dispatch Date & Time: ${new Date().toLocaleString('en-IN')}`, 14, 45);
    doc.text(`Case Reference: ${caseDetails.case_id}`, 14, 53);
    doc.text(`Target Assigned Unit: ${caseDetails.dispatch_unit}`, 14, 61);

    // Horizontal Rule
    doc.setDrawColor(203, 213, 225);
    doc.line(14, 66, 196, 66);

    // Critical Suspect Details
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.setTextColor(220, 38, 38); // Red
    doc.text('1. ACTIVE INTERCEPTION TARGET', 14, 76);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(51, 65, 85);
    doc.text(`Primary Suspect / Mule Account: ${caseDetails.mule_account}`, 14, 85);
    doc.text(`Compromised Sum in Flight: INR ${Number(caseDetails.compromised_amount).toLocaleString('en-IN')}`, 14, 93);
    doc.text(`Predicted Cashout Window: ${caseDetails.time_window} (URGENT)`, 14, 101);

    // Target Location
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.setTextColor(15, 23, 42);
    doc.text('2. PREDICTED CASHOUT POINT (RANK #1 ATM)', 14, 115);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Location: ${caseDetails.top_atm}`, 14, 124);
    doc.text('Operational Instructions:', 14, 132);
    doc.text('- Deploy quick-reaction patrol to the above physical kiosk immediately.', 18, 140);
    doc.text('- Observe for individuals attempting multiple rapid debit-card withdrawals.', 18, 148);
    doc.text('- Secure CCTV footage timestamp and report outcome to Central Command.', 18, 156);

    // Official Stamp box
    doc.setDrawColor(220, 38, 38);
    doc.setLineWidth(1);
    doc.rect(130, 180, 65, 30);
    doc.setFontSize(9);
    doc.setTextColor(220, 38, 38);
    doc.setFont('helvetica', 'bold');
    doc.text('AUTHORIZED DISPATCH', 135, 190);
    doc.text('I4C CYBER COMMAND', 135, 198);
    doc.text(`DIGITAL STAMP: DRISHTI-${Date.now().toString().slice(-6)}`, 135, 204);

    doc.save(`Dispatch_Order_${caseDetails.case_id}.pdf`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h3 className="font-mono font-bold text-sm text-slate-100">
              POLICE DISPATCH ORDER PREVIEW
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-3 text-xs font-mono text-slate-300">
          <p className="text-slate-400">
            Generate an official court-admissible & field-ready dispatch sheet for quick response patrol teams.
          </p>

          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <div><span className="text-slate-500">CASE ID:</span> <span className="text-white">{caseDetails.case_id}</span></div>
            <div><span className="text-slate-500">MULE:</span> <span className="text-red-400 font-bold">{caseDetails.mule_account}</span></div>
            <div><span className="text-slate-500">TARGET ATM:</span> <span className="text-cyan-300">{caseDetails.top_atm}</span></div>
            <div><span className="text-slate-500">ACTION WINDOW:</span> <span className="text-amber-400 font-bold">{caseDetails.time_window}</span></div>
          </div>
        </div>

        <div className="p-4 bg-slate-950/80 border-t border-slate-800 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={generatePDF}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-slate-950 transition-all shadow-lg shadow-cyan-500/30 cursor-pointer"
          >
            <FileDown className="w-4 h-4" />
            <span>Generate & Download PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PoliceDispatchModal;

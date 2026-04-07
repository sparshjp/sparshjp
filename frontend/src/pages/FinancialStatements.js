import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, TrendingUp, TrendingDown, ChevronDown, ChevronRight, IndianRupee, FileSpreadsheet } from 'lucide-react';
import { API } from '../App';

function downloadExport(endpoint, filename) {
  const url = `${API}/financial-statements/${endpoint}`;
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function formatINR(num) {
  if (num === undefined || num === null) return '—';
  const abs = Math.abs(num);
  if (abs >= 10000000) return `${(num / 10000000).toFixed(2)} Cr`;
  if (abs >= 100000) return `${(num / 100000).toFixed(2)} L`;
  return new Intl.NumberFormat('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(num);
}

function BSLineItem({ label, amount, note, indent = 0, isBold = false, isTotal = false, children, details }) {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = (children && children.length > 0) || (details && Object.keys(details).length > 0);

  return (
    <>
      <tr
        className={`border-b border-[#1B2D42]/40 ${isTotal ? 'bg-[#152236]/50 font-semibold' : 'hover:bg-[#152236]/30'} transition-colors cursor-default`}
        onClick={() => hasChildren && setExpanded(!expanded)}
        data-testid={`bs-row-${label?.replace(/[^a-zA-Z0-9]/g, '-')}`}
      >
        <td className={`py-2.5 px-4 ${isBold ? 'font-semibold text-[#00C9A7]' : 'text-[#E8EDF2]'}`} style={{ paddingLeft: `${16 + indent * 24}px` }}>
          <div className="flex items-center gap-2">
            {hasChildren && (expanded ? <ChevronDown className="w-3.5 h-3.5 text-[#4A5B6E]" /> : <ChevronRight className="w-3.5 h-3.5 text-[#4A5B6E]" />)}
            {isTotal && <div className="w-8 h-0.5 bg-[#00C9A7]/40 mr-1" />}
            {label}
          </div>
        </td>
        <td className="py-2.5 px-2 text-center text-[#4A5B6E] text-xs">{note || ''}</td>
        <td className={`py-2.5 px-4 text-right font-mono ${isTotal ? 'text-[#00C9A7] font-bold text-base' : amount < 0 ? 'text-[#FF4D6A]' : 'text-[#E8EDF2]'}`}>
          {amount !== undefined ? formatINR(amount) : ''}
        </td>
      </tr>
      {expanded && details && Object.entries(details).map(([key, val]) => (
        <tr key={key} className="border-b border-[#1B2D42]/20 bg-[#0D1B2A]/40">
          <td className="py-1.5 px-4 text-[#4A5B6E] text-xs italic" style={{ paddingLeft: `${40 + indent * 24}px` }}>{key.replace(/_/g, ' ')}</td>
          <td></td>
          <td className="py-1.5 px-4 text-right font-mono text-xs text-[#7A8BA0]">{formatINR(val)}</td>
        </tr>
      ))}
    </>
  );
}

function PLLineItem({ sl, particular, amount, note, isTotal, isHeader, isFinal, details }) {
  const [expanded, setExpanded] = useState(false);
  const hasDetails = details && details.length > 0;

  return (
    <>
      <tr
        className={`border-b border-[#1B2D42]/40 transition-colors ${
          isFinal ? 'bg-[#00C9A7]/10 border-[#00C9A7]/30' :
          isTotal ? 'bg-[#1B2D42]/30' :
          isHeader ? 'bg-[#1B2D42]/20' : 'hover:bg-[#1B2D42]/20'
        } ${hasDetails ? 'cursor-pointer' : ''}`}
        onClick={() => hasDetails && setExpanded(!expanded)}
        data-testid={`pl-row-${particular?.replace(/[^a-zA-Z0-9]/g, '-')}`}
      >
        <td className={`py-2.5 px-4 font-mono ${sl ? 'text-[#00C9A7] font-semibold' : 'text-[#4A5B6E]'} w-16`}>{sl}</td>
        <td className={`py-2.5 px-4 ${isHeader || isTotal || isFinal ? 'font-semibold text-[#00C9A7]' : 'text-[#E8EDF2]'}`}>
          <div className="flex items-center gap-2">
            {hasDetails && (expanded ? <ChevronDown className="w-3.5 h-3.5 text-[#4A5B6E]" /> : <ChevronRight className="w-3.5 h-3.5 text-[#4A5B6E]" />)}
            {particular}
          </div>
        </td>
        <td className="py-2.5 px-2 text-center text-[#4A5B6E] text-xs w-12">{note || ''}</td>
        <td className={`py-2.5 px-4 text-right font-mono w-36 ${
          isFinal ? 'text-lg font-bold' :
          isTotal ? 'font-bold' : ''
        } ${amount < 0 ? 'text-[#FF4D6A]' : isFinal || isTotal ? 'text-[#00C9A7]' : 'text-[#E8EDF2]'}`}>
          {amount !== undefined && !isHeader ? formatINR(amount) : ''}
        </td>
      </tr>
      {expanded && details && details.map((d, i) => (
        <tr key={i} className="border-b border-[#1B2D42]/20 bg-[#152236]/40">
          <td></td>
          <td className="py-1.5 px-4 text-[#4A5B6E] text-xs italic pl-12">{d.account}</td>
          <td></td>
          <td className="py-1.5 px-4 text-right font-mono text-xs text-[#7A8BA0]">{formatINR(d.amount)}</td>
        </tr>
      ))}
    </>
  );
}

export default function FinancialStatements() {
  const [activeTab, setActiveTab] = useState('balance-sheet');
  const [bsData, setBsData] = useState(null);
  const [plData, setPlData] = useState(null);
  const [tbData, setTbData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [company, setCompany] = useState({});

  useEffect(() => {
    fetch(`${API}/company/settings`).then(r => r.ok ? r.json() : {}).then(setCompany).catch(() => {});
  }, []);

  useEffect(() => {
    loadReport(activeTab);
  }, [activeTab]);

  async function loadReport(tab) {
    setLoading(true);
    try {
      const endpoint = tab === 'balance-sheet' ? 'balance-sheet' :
                       tab === 'profit-loss' ? 'profit-and-loss' : 'trial-balance';
      const r = await fetch(`${API}/financial-statements/${endpoint}`);
      if (!r.ok) throw new Error(`Failed: ${r.status}`);
      const data = await r.json();
      if (tab === 'balance-sheet') setBsData(data);
      else if (tab === 'profit-loss') setPlData(data);
      else setTbData(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  const tabs = [
    { id: 'balance-sheet', label: 'Balance Sheet', icon: FileText },
    { id: 'profit-loss', label: 'Profit & Loss', icon: TrendingUp },
    { id: 'trial-balance', label: 'Trial Balance', icon: IndianRupee },
  ];

  return (
    <div className="space-y-6" data-testid="financial-statements-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {company.logo_url && (
            <img src={`${API}${company.logo_url}`} alt="Logo" className="w-10 h-10 rounded-lg object-cover border border-[#1B2D42]" data-testid="fs-company-logo" />
          )}
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">Financial Statements</h1>
            <p className="text-[#4A5B6E] text-sm mt-1">
              {company.legal_name || 'Company Name'} — Schedule III, Companies Act 2013
            </p>
            {company.gstin && <p className="text-[#4A5B6E] text-[10px] font-mono mt-0.5">GSTIN: {company.gstin} | CIN: {company.cin || '—'}</p>}
          </div>
        </div>
        <div className="flex gap-2">
          {activeTab === 'balance-sheet' && (
            <button data-testid="fs-download-bs" onClick={() => downloadExport('balance-sheet/export/excel', 'Balance_Sheet_Schedule_III.xlsx')}
              className="flex items-center gap-2 px-3 py-2 bg-[#152236] border border-[#1B2D42] text-[#7A8BA0] hover:text-[#00C9A7] hover:border-[#00C9A7]/30 rounded-lg text-xs font-medium transition-colors">
              <FileSpreadsheet size={14} /> Download Excel
            </button>
          )}
          {activeTab === 'profit-loss' && (
            <button data-testid="fs-download-pl" onClick={() => downloadExport('profit-and-loss/export/excel', 'Profit_Loss_Schedule_III.xlsx')}
              className="flex items-center gap-2 px-3 py-2 bg-[#152236] border border-[#1B2D42] text-[#7A8BA0] hover:text-[#00C9A7] hover:border-[#00C9A7]/30 rounded-lg text-xs font-medium transition-colors">
              <FileSpreadsheet size={14} /> Download Excel
            </button>
          )}
          {activeTab === 'trial-balance' && (
            <button data-testid="fs-download-tb" onClick={() => downloadExport('trial-balance/export/excel', 'Trial_Balance.xlsx')}
              className="flex items-center gap-2 px-3 py-2 bg-[#152236] border border-[#1B2D42] text-[#7A8BA0] hover:text-[#00C9A7] hover:border-[#00C9A7]/30 rounded-lg text-xs font-medium transition-colors">
              <FileSpreadsheet size={14} /> Download Excel
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#152236] p-1 rounded-lg w-fit" data-testid="fs-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            data-testid={`fs-tab-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-[#00C9A7]/20 text-[#00C9A7] border border-[#00C9A7]/30'
                : 'text-[#7A8BA0] hover:text-[#E8EDF2] hover:bg-[#1B2D42]'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <div className="text-[#4A5B6E] py-8 text-center">Loading...</div>}

      {/* Balance Sheet */}
      {activeTab === 'balance-sheet' && bsData && (
        <div className="space-y-6" data-testid="balance-sheet-content">
          {/* Company Header */}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6 text-center">
            {company.logo_url && (
              <img src={`${API}${company.logo_url}`} alt="Logo" className="w-14 h-14 rounded-lg object-cover border border-[#1B2D42] mx-auto mb-3" data-testid="bs-company-logo" />
            )}
            <h2 className="text-lg font-bold text-[#E8EDF2]">{bsData.company_name}</h2>
            <p className="text-[#7A8BA0] text-sm">Balance Sheet as at {bsData.as_of_date}</p>
            <p className="text-[#4A5B6E] text-xs mt-1">{bsData.format}</p>
            <div className={`mt-3 inline-block px-3 py-1 rounded-full text-xs font-medium ${
              bsData.is_balanced ? 'bg-[#00C9A7]/20 text-[#00C9A7]' : 'bg-[#FF4D6A]/20 text-[#FF4D6A]'
            }`}>
              {bsData.is_balanced ? 'Balanced' : `Out of balance by ${formatINR(bsData.difference)}`}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* EQUITY & LIABILITIES */}
            <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
              <div className="bg-[#1B2D42]/50 px-4 py-3 border-b border-[#1B2D42]">
                <h3 className="text-sm font-bold text-[#00C9A7] tracking-wider">I. EQUITY AND LIABILITIES</h3>
              </div>
              <table className="w-full text-sm" data-testid="bs-equity-liabilities-table">
                <thead>
                  <tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs">
                    <th className="py-2 px-4 text-left">Particulars</th>
                    <th className="py-2 px-2 text-center w-12">Note</th>
                    <th className="py-2 px-4 text-right w-32">Amount (INR)</th>
                  </tr>
                </thead>
                <tbody>
                  <BSLineItem label="1. Shareholders' Funds" isBold />
                  <BSLineItem label="(a) Share Capital" amount={bsData.equity_and_liabilities.shareholders_funds.share_capital.amount} note={1} indent={1} />
                  <BSLineItem label="(b) Reserves and Surplus" amount={bsData.equity_and_liabilities.shareholders_funds.reserves_and_surplus.amount} note={2} indent={1}
                    details={bsData.equity_and_liabilities.shareholders_funds.reserves_and_surplus.details} />
                  <BSLineItem label="Total Shareholders' Funds" amount={bsData.equity_and_liabilities.shareholders_funds.total} isTotal indent={1} />

                  <BSLineItem label="3. Non-current Liabilities" isBold />
                  <BSLineItem label="(a) Long-term Borrowings" amount={bsData.equity_and_liabilities.non_current_liabilities.long_term_borrowings.amount} note={3} indent={1} />
                  <BSLineItem label="Total Non-current Liabilities" amount={bsData.equity_and_liabilities.non_current_liabilities.total} isTotal indent={1} />

                  <BSLineItem label="4. Current Liabilities" isBold />
                  <BSLineItem label="(b) Trade Payables" amount={bsData.equity_and_liabilities.current_liabilities.trade_payables.amount} note={4} indent={1} />
                  <BSLineItem label="(c) Other Current Liabilities" amount={bsData.equity_and_liabilities.current_liabilities.other_current_liabilities.amount} note={5} indent={1} />
                  <BSLineItem label="Total Current Liabilities" amount={bsData.equity_and_liabilities.current_liabilities.total} isTotal indent={1} />

                  <BSLineItem label="TOTAL EQUITY & LIABILITIES" amount={bsData.equity_and_liabilities.total} isTotal />
                </tbody>
              </table>
            </div>

            {/* ASSETS */}
            <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
              <div className="bg-[#1B2D42]/50 px-4 py-3 border-b border-[#1B2D42]">
                <h3 className="text-sm font-bold text-[#00C9A7] tracking-wider">II. ASSETS</h3>
              </div>
              <table className="w-full text-sm" data-testid="bs-assets-table">
                <thead>
                  <tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs">
                    <th className="py-2 px-4 text-left">Particulars</th>
                    <th className="py-2 px-2 text-center w-12">Note</th>
                    <th className="py-2 px-4 text-right w-32">Amount (INR)</th>
                  </tr>
                </thead>
                <tbody>
                  <BSLineItem label="1. Non-current Assets" isBold />
                  <BSLineItem label="(a) Property, Plant & Equipment" amount={bsData.assets.non_current_assets.property_plant_equipment.net_block} note={6} indent={1}
                    details={{
                      gross_block: bsData.assets.non_current_assets.property_plant_equipment.gross_block,
                      less_accumulated_depreciation: -bsData.assets.non_current_assets.property_plant_equipment.accumulated_depreciation,
                    }} />
                  <BSLineItem label="(e) Other Non-current Assets" amount={bsData.assets.non_current_assets.other_non_current_assets.amount} note={7} indent={1} />
                  <BSLineItem label="Total Non-current Assets" amount={bsData.assets.non_current_assets.total} isTotal indent={1} />

                  <BSLineItem label="2. Current Assets" isBold />
                  <BSLineItem label="(b) Inventories" amount={bsData.assets.current_assets.inventories.amount} note={8} indent={1}
                    details={bsData.assets.current_assets.inventories.details} />
                  <BSLineItem label="(c) Trade Receivables" amount={bsData.assets.current_assets.trade_receivables.amount} note={9} indent={1} />
                  <BSLineItem label="(d) Cash and Cash Equivalents" amount={bsData.assets.current_assets.cash_and_equivalents.amount} note={10} indent={1} />
                  <BSLineItem label="(e) Short-term Loans & Advances" amount={bsData.assets.current_assets.short_term_loans_advances.amount} indent={1} />
                  <BSLineItem label="Total Current Assets" amount={bsData.assets.current_assets.total} isTotal indent={1} />

                  <BSLineItem label="TOTAL ASSETS" amount={bsData.assets.total} isTotal />
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Profit & Loss */}
      {activeTab === 'profit-loss' && plData && (
        <div className="space-y-6" data-testid="profit-loss-content">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6 text-center">
            {company.logo_url && (
              <img src={`${API}${company.logo_url}`} alt="Logo" className="w-14 h-14 rounded-lg object-cover border border-[#1B2D42] mx-auto mb-3" />
            )}
            <h2 className="text-lg font-bold text-[#E8EDF2]">{plData.company_name}</h2>
            <p className="text-[#7A8BA0] text-sm">Statement of Profit and Loss for the period {plData.period?.from} to {plData.period?.to}</p>
            <p className="text-[#4A5B6E] text-xs mt-1">{plData.format}</p>
            <div className="flex justify-center gap-4 mt-3">
              <span className="text-sm text-[#7A8BA0]">Net: <span className={plData.summary?.net_profit >= 0 ? 'text-[#00C9A7] font-bold' : 'text-[#FF4D6A] font-bold'}>{formatINR(plData.summary?.net_profit)}</span></span>
              <span className="text-sm text-[#7A8BA0]">Margin: <span className="text-[#00C9A7] font-bold">{plData.summary?.gross_margin_pct}%</span></span>
            </div>
          </div>

          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
            <table className="w-full text-sm" data-testid="pl-table">
              <thead>
                <tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
                  <th className="py-2.5 px-4 text-left w-16">Sl.</th>
                  <th className="py-2.5 px-4 text-left">Particulars</th>
                  <th className="py-2.5 px-2 text-center w-12">Note</th>
                  <th className="py-2.5 px-4 text-right w-36">Amount (INR)</th>
                </tr>
              </thead>
              <tbody>
                {plData.line_items?.map((item, i) => (
                  <PLLineItem key={i} {...item} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Trial Balance */}
      {activeTab === 'trial-balance' && tbData && (
        <div className="space-y-6" data-testid="trial-balance-content">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6 text-center">
            {company.logo_url && (
              <img src={`${API}${company.logo_url}`} alt="Logo" className="w-14 h-14 rounded-lg object-cover border border-[#1B2D42] mx-auto mb-3" />
            )}
            <h2 className="text-lg font-bold text-[#E8EDF2]">{tbData.company_name}</h2>
            <p className="text-[#7A8BA0] text-sm">Trial Balance as at {tbData.as_of_date}</p>
            <div className={`mt-3 inline-block px-3 py-1 rounded-full text-xs font-medium ${
              tbData.in_balance ? 'bg-[#00C9A7]/20 text-[#00C9A7]' : 'bg-[#FF4D6A]/20 text-[#FF4D6A]'
            }`}>
              {tbData.in_balance ? 'In Balance' : `Out by ${formatINR(tbData.difference)}`}
            </div>
          </div>

          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
            <table className="w-full text-sm" data-testid="tb-table">
              <thead>
                <tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
                  <th className="py-2.5 px-4 text-left">Account</th>
                  <th className="py-2.5 px-4 text-left w-24">Category</th>
                  <th className="py-2.5 px-4 text-right w-32">Debit (INR)</th>
                  <th className="py-2.5 px-4 text-right w-32">Credit (INR)</th>
                </tr>
              </thead>
              <tbody>
                {tbData.entries?.map((entry, i) => (
                  <tr key={i} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20 transition-colors">
                    <td className="py-2 px-4 text-[#E8EDF2]">{entry.account}</td>
                    <td className="py-2 px-4 text-[#4A5B6E] text-xs">{entry.category}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{entry.debit > 0 ? formatINR(entry.debit) : ''}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{entry.credit > 0 ? formatINR(entry.credit) : ''}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-[#1B2D42]/50 border-t-2 border-[#00C9A7]/30">
                  <td className="py-3 px-4 font-bold text-[#00C9A7]" colSpan={2}>TOTAL</td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-[#00C9A7]">{formatINR(tbData.total_debit)}</td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-[#00C9A7]">{formatINR(tbData.total_credit)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

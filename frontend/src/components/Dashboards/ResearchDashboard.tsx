'use client';

import React, { useState } from 'react';
import { FileText, Download, ShieldAlert, Users, TrendingUp, HelpCircle } from 'lucide-react';

interface GeopoliticalEvent {
  id: string;
  title: string;
  date: string;
  summary: string;
  whatHappened: string;
  whyItMatters: string;
  whoBenefits: string;
  whoLoses: string;
  indiaImpact: string[];
}

const GEOPOLITICAL_EVENTS: GeopoliticalEvent[] = [
  {
    id: 'redsea',
    title: 'Red Sea Maritime Corridor Disruptions',
    date: 'June 2026',
    summary: 'Attacks on merchant vessels in the Bab-el-Mandeb Strait force major container conglomerates to reroute around Africa’s Cape of Good Hope, doubling shipping times and boosting spot freight rates.',
    whatHappened: 'Cargo ships in the Red Sea shipping canal faced drone and missile strikes, prompting container majors (Maersk, Hapag-Lloyd) to halt Suez routes and detour around Africa.',
    whyItMatters: 'The Suez Canal routes 12% of global trade. Deterring shipping adds 10-14 days to journey times, compressing container availability and spiking global freight logistics costs.',
    whoBenefits: 'Ocean shipping carriers (due to 150%+ spikes in freight rates), air cargo transit companies.',
    whoLoses: 'European importers of Asian electronics; agricultural exporters facing shipping delays.',
    indiaImpact: [
      'Export Cost Inflation: Freight costs to Europe and the US East Coast have surged by 80-100%, hurting Indian textile and auto part exporters.',
      'Import Delays: Key engineering machinery imports face delayed schedules of 2-3 weeks.',
      'Trade Deficit Pressure: Rising logistics expenses inflate the overall merchandise import balance.'
    ]
  },
  {
    id: 'ustrade',
    title: 'US-China Semiconductor & EV Trade Restrictions',
    date: 'May 2026',
    summary: 'The United States implements aggressive tariff packages (100% on EVs, 50% on solar cells) and tightens export controls on advanced lithography machinery to China.',
    whatHappened: 'US regulators announced enhanced tariffs targeting key Chinese green-tech items and restricted high-end AI processor sales to Chinese technology firms.',
    whyItMatters: 'Forces a rapid decoupling of the global hardware technology supply chain, pushing countries to seek non-aligned manufacturing hubs ("China + 1").',
    whoBenefits: 'Domestic tech manufacturers in India, Vietnam, and Mexico; Western semiconductor equipment designers.',
    whoLoses: 'Chinese electronics companies; global consumers facing higher supply prices.',
    indiaImpact: [
      'FDI Inflow: Accelerates investments under India\'s Rs 76,000-crore semiconductor PLI scheme.',
      'Hardware Assembly Tailwind: EMS firms (e.g. Dixon Technologies) see increased manufacturing orders.',
      'Sourcing Risks: Squeezes cheap raw solar cell imports for Indian renewable energy projects.'
    ]
  },
  {
    id: 'opec',
    title: 'OPEC+ Crude Supply Voluntary Extensions',
    date: 'April 2026',
    summary: 'OPEC+ oil ministers agree to sustain voluntary crude production cuts of 2.2 million barrels per day through the end of the year to support global oil prices.',
    whatHappened: 'Saudi Arabia and allied oil nations prolonged active output caps, balancing out record US shale production volumes.',
    whyItMatters: 'Ensures Brent crude oil prices remain anchored above $80/bbl, preventing price collapses despite cooling global industrial indicators.',
    whoBenefits: 'Sovereign oil exporters, upstream domestic extraction firms (ONGC, Oil India).',
    whoLoses: 'Net energy importing countries, retail fuel consumers.',
    indiaImpact: [
      'Imported Inflation: India imports 85% of crude. Prolonged high Brent keeps transport and fuel costs high.',
      'Current Account Deficit: Widens India\'s CAD by approximately $8 billion for every sustained $10 crude premium.',
      'Currency Pressure: Sustained USD demand for oil purchases keeps the Rupee pinned at weaker thresholds.'
    ]
  }
];

export default function ResearchDashboard() {
  const [selectedEventId, setSelectedEventId] = useState('redsea');
  const [reportGenerated, setReportGenerated] = useState(false);
  const [generating, setGenerating] = useState(false);

  const event = GEOPOLITICAL_EVENTS.find(e => e.id === selectedEventId) || GEOPOLITICAL_EVENTS[0];

  const handleGenerateReport = () => {
    setGenerating(true);
    setReportGenerated(false);
    setTimeout(() => {
      setGenerating(false);
      setReportGenerated(true);
    }, 1200);
  };

  const printReport = () => {
    window.print();
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 h-full overflow-y-auto pr-1">
      {/* Geopolitical Timeline List Left Panel */}
      <div className="border border-gray-800 rounded bg-[#090d16]/30 p-2.5 flex flex-col gap-2.5 lg:col-span-1 min-h-[250px]">
        <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1.5 flex items-center">
          <ShieldAlert className="w-4 h-4 text-red-500 mr-1.5" />
          GEOPOLITICAL INTELLIGENCE TIMELINE
        </h3>
        
        <div className="space-y-2 flex-1">
          {GEOPOLITICAL_EVENTS.map((e) => {
            const isSelected = selectedEventId === e.id;
            return (
              <div
                key={e.id}
                onClick={() => {
                  setSelectedEventId(e.id);
                  setReportGenerated(false);
                }}
                className={`p-2 rounded cursor-pointer transition-colors border flex flex-col ${
                  isSelected ? 'bg-red-950/20 border-red-500/50' : 'bg-gray-950/20 border-transparent hover:bg-gray-800/30'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold text-gray-200 truncate max-w-[80%]">{e.title}</span>
                  <span className="text-[8px] text-gray-500 font-sans">{e.date}</span>
                </div>
                <p className="text-[8.5px] text-gray-500 font-sans line-clamp-2 leading-tight">
                  {e.summary}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Deep Geopolitical Intelligence Details Panel */}
      <div className="lg:col-span-3 flex flex-col gap-3 min-h-[350px]">
        <div className="terminal-panel p-4 flex-1 flex flex-col justify-between">
          
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-850 pb-2 mb-3">
            <div className="flex items-center gap-1.5">
              <span className="text-gray-300 font-bold text-xs uppercase">Geopolitical Risk Analysis</span>
            </div>
            <span className="text-[9px] text-gray-500">
              Analysis Date: {event.date}
            </span>
          </div>

          {/* Event Content Details */}
          <div className="flex-1 space-y-4">
            <h2 className="text-sm font-bold text-red-400 uppercase tracking-tight flex items-center">
              <ShieldAlert className="w-4 h-4 mr-1.5" />
              {event.title}
            </h2>

            {/* Core detail points */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs text-gray-400">
              <div className="space-y-3">
                <div>
                  <span className="text-[9px] text-gray-500 font-bold block mb-1 uppercase">What Happened:</span>
                  <p className="leading-relaxed">{event.whatHappened}</p>
                </div>
                <div>
                  <span className="text-[9px] text-gray-500 font-bold block mb-1 uppercase">Why It Matters:</span>
                  <p className="leading-relaxed">{event.whyItMatters}</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div className="border border-emerald-950 bg-emerald-950/10 rounded p-2">
                    <span className="text-[9px] text-emerald-400 font-bold block mb-1 flex items-center uppercase">
                      <Users className="w-3.5 h-3.5 mr-1" />
                      Who Benefits:
                    </span>
                    <p className="text-[11px] text-gray-300 leading-normal">{event.whoBenefits}</p>
                  </div>
                  <div className="border border-red-955 bg-red-955/10 rounded p-2">
                    <span className="text-[9px] text-red-400 font-bold block mb-1 flex items-center uppercase">
                      <Users className="w-3.5 h-3.5 mr-1" />
                      Who Loses:
                    </span>
                    <p className="text-[11px] text-gray-300 leading-normal">{event.whoLoses}</p>
                  </div>
                </div>

                {/* India Impact Box */}
                <div className="border border-gray-800 rounded p-2.5 bg-gray-900/10">
                  <span className="text-[9px] text-gray-500 font-bold block mb-1.5 uppercase flex items-center">
                    <TrendingUp className="w-3.5 h-3.5 text-blue-400 mr-1.5" />
                    Domestic Transmission to India:
                  </span>
                  <ul className="space-y-1.5 pl-3 list-none">
                    {event.indiaImpact.map((imp, i) => (
                      <li key={i} className="text-gray-350 relative text-[11px] leading-relaxed pl-2">
                        <span className="absolute left-0 top-1.5 w-1 h-1 bg-red-500 rounded-full"></span>
                        {imp}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex justify-between items-center border-t border-gray-850 pt-3 mt-3">
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-[10px] font-bold uppercase transition-colors"
            >
              <FileText className="w-3.5 h-3.5" />
              {generating ? 'Compiling Report...' : 'Compile Executive Report'}
            </button>

            {reportGenerated && (
              <button
                onClick={printReport}
                className="flex items-center gap-1.5 text-[10px] font-bold text-gray-400 hover:text-gray-200"
              >
                <Download className="w-4 h-4" /> Print / Export Report
              </button>
            )}
          </div>

        </div>

        {/* Printable Executive Report Modal Overlay (Simulated output card) */}
        {reportGenerated && (
          <div className="border border-yellow-500/40 rounded p-4 bg-yellow-950/5 text-xs text-gray-300 font-mono space-y-3">
            <div className="flex justify-between border-b border-yellow-950 pb-2">
              <span className="font-bold text-yellow-400 uppercase tracking-widest text-sm flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                EXECUTIVE INTELLIGENCE BRIEFING: {event.title}
              </span>
              <span className="text-[10px] text-gray-500">BRIEFING ID: #GIR-0{event.id.toUpperCase()}</span>
            </div>

            <div className="space-y-2.5">
              <div>
                <span className="font-bold text-gray-400 block uppercase text-[10px]">1. Scope & Trigger:</span>
                <p className="leading-relaxed pl-3 border-l border-gray-800 text-[11px]">
                  {event.whatHappened}
                </p>
              </div>
              
              <div>
                <span className="font-bold text-gray-400 block uppercase text-[10px]">2. Sovereign Risk Vulnerabilities:</span>
                <p className="leading-relaxed pl-3 border-l border-gray-800 text-[11px]">
                  The disruption triggers immediate structural changes in logistics pathways. Shipping lanes are congested, inflating container rates by double-digits. Exporters face compressed margins and shipping delays.
                </p>
              </div>

              <div>
                <span className="font-bold text-gray-400 block uppercase text-[10px]">3. India Transmission Impact (Immediate):</span>
                <ul className="list-disc pl-6 space-y-1 text-[11px]">
                  {event.indiaImpact.map((imp, idx) => (
                    <li key={idx}>{imp}</li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div className="text-[9px] text-gray-600 border-t border-gray-900 pt-1.5 text-right font-sans">
              CONFIDENTIAL - FOR RESEARCH & ANALYTICAL PURPOSES ONLY.
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, Compass, Search, BarChart2, TrendingUp, HelpCircle } from 'lucide-react';

interface PortDetails {
  port: string;
  traffic_TEU: number;
  growth_yoy: number;
  congestion_status: string;
}

interface SatelliteDetails {
  index: number;
  status: string;
  yoy_change: number;
}

interface TrendDetails {
  query_volume: number;
  weekly_trend: string;
  significance: string;
}

interface JobDetails {
  posting_index: number;
  yoy_change: number;
  sentiment: string;
}

interface FundingHistory {
  date: string;
  volume_usd_m: number;
  deal_count: number;
}

interface AlternativeData {
  port_traffic: PortDetails[];
  satellite_activity: Record<string, SatelliteDetails>;
  google_trends: Record<string, TrendDetails>;
  job_market: Record<string, JobDetails>;
  startup_funding: {
    latest_volume_usd_m: number;
    latest_deal_count: number;
    history: FundingHistory[];
  };
  last_updated: string;
}

export default function GovernmentDashboard() {
  const [data, setData] = useState<AlternativeData | null>(null);

  useEffect(() => {
    const fetchAlternativeData = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/economy/alternative');
        if (!resp.ok) throw new Error('API server error');
        const resData = await resp.json();
        setData(resData);
      } catch (e) {
        console.error("Failed to load alternative data:", e);
      }
    };

    fetchAlternativeData();
  }, []);

  // Custom SVG line chart for Startup VC Funding
  const renderFundingChart = () => {
    if (!data || !data.startup_funding || data.startup_funding.history.length === 0) return null;
    const history = [...data.startup_funding.history].reverse(); // Oldest to newest

    const width = 450;
    const height = 130;
    const paddingLeft = 35;
    const paddingRight = 10;
    const paddingTop = 10;
    const paddingBottom = 20;

    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;

    const values = history.map(h => h.volume_usd_m);
    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const range = maxVal - minVal;

    const yMax = maxVal + (range * 0.1 || 100);
    const yMin = Math.max(0, minVal - (range * 0.1 || 100));
    const yRange = yMax - yMin;

    const getX = (index: number) => paddingLeft + (index * (chartWidth / (history.length - 1)));
    const getY = (val: number) => paddingTop + chartHeight - (((val - yMin) / yRange) * chartHeight);

    let pathD = '';
    history.forEach((point, idx) => {
      const x = getX(idx);
      const y = getY(point.volume_usd_m);
      if (idx === 0) pathD = `M ${x} ${y}`;
      else pathD += ` L ${x} ${y}`;
    });

    return (
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${height}`}>
        {/* Grids */}
        {[0, 0.5, 1].map((ratio, idx) => {
          const val = yMin + (yRange * ratio);
          const y = getY(val);
          return (
            <g key={idx}>
              <line x1={paddingLeft} y1={y} x2={width - paddingRight} y2={y} stroke="#111827" strokeWidth="0.5" strokeDasharray="2,2" />
              <text x={paddingLeft - 5} y={y + 3} textAnchor="end" fill="#4b5563" className="text-[8px] font-mono">
                ${Math.round(val)}M
              </text>
            </g>
          );
        })}

        {/* Date labels */}
        {history.map((h, idx) => {
          if (idx === 0 || idx === history.length - 1 || idx === Math.floor(history.length / 2)) {
            const x = getX(idx);
            return (
              <text key={idx} x={x} y={height - 4} textAnchor="middle" fill="#4b5563" className="text-[8px] font-mono">
                {h.date}
              </text>
            );
          }
          return null;
        })}

        {/* Shaded Area */}
        <path
          d={`${pathD} L ${getX(history.length - 1)} ${paddingTop + chartHeight} L ${getX(0)} ${paddingTop + chartHeight} Z`}
          fill="url(#funding-grad)"
        />

        {/* Path line */}
        <path d={pathD} fill="none" stroke="#10b981" strokeWidth="1.5" />

        {/* Nodes */}
        {history.map((h, idx) => {
          const x = getX(idx);
          const y = getY(h.volume_usd_m);
          return (
            <circle
              key={idx}
              cx={x}
              cy={y}
              r={2.5}
              fill="#064e3b"
              stroke="#10b981"
              strokeWidth="0.5"
            />
          );
        })}

        <defs>
          <linearGradient id="funding-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 h-full overflow-y-auto pr-1">
      
      {/* Port Traffic & Industrial Satellite Left Columns */}
      <div className="lg:col-span-2 flex flex-col gap-3">
        {/* Port Traffic */}
        <div className="terminal-panel p-3">
          <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-2.5 flex items-center">
            <Compass className="w-3.5 h-3.5 text-blue-500 mr-1.5" />
            REAL-TIME SHIPPING PORT TRAFFIC & CONTAINER CONGESTION
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-850 text-[9px] text-gray-500 uppercase">
                  <th className="py-1">Major Sea Port</th>
                  <th className="py-1">Monthly Traffic (TEUs)</th>
                  <th className="py-1">YoY Growth</th>
                  <th className="py-1 text-center">Congestion Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-900 text-[10px]">
                {data?.port_traffic.map((port, idx) => {
                  const isUp = port.growth_yoy >= 0;
                  const cStatus = port.congestion_status;
                  return (
                    <tr key={idx} className="hover:bg-gray-950/25">
                      <td className="py-2 text-gray-300 font-bold">{port.port}</td>
                      <td className="py-2 text-gray-300">{port.traffic_TEU.toLocaleString()} TEUs</td>
                      <td className={`py-2 font-bold ${isUp ? 'text-emerald-500' : 'text-red-500'}`}>
                        {isUp ? '+' : ''}{port.growth_yoy}%
                      </td>
                      <td className="py-2 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                          cStatus === 'Low' ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-900/40' : 
                          cStatus === 'Normal' ? 'bg-blue-950/50 text-blue-400 border border-blue-900/40' : 
                          'bg-red-955/50 text-red-400 border border-red-900/40'
                        }`}>
                          {cStatus}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Satellite Industrial Activity */}
        <div className="terminal-panel p-3 flex-1">
          <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-2.5 flex items-center">
            <Cpu className="w-3.5 h-3.5 text-emerald-500 mr-1.5" />
            SATELLITE SPECTRAL INDUSTRIAL NIGHT-LIGHT INDEX
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {data && Object.entries(data.satellite_activity).map(([zone, detail]) => {
              const isUp = detail.yoy_change >= 0;
              return (
                <div key={zone} className="border border-gray-800 bg-[#070b13]/50 p-2.5 rounded flex flex-col justify-between">
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="text-[10.5px] font-bold text-gray-200">{zone}</span>
                    <span className={`text-[9px] font-semibold px-1.5 py-0.2 bg-gray-900 rounded ${
                      detail.status.includes('High') || detail.status.includes('Peak') ? 'text-emerald-400' : 'text-yellow-400'
                    }`}>
                      {detail.status}
                    </span>
                  </div>

                  <div className="flex justify-between items-end">
                    <div>
                      <span className="text-[8px] text-gray-500 block uppercase">Night light Index</span>
                      <span className="text-sm font-bold text-gray-300">{detail.index}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[8px] text-gray-500 block uppercase">YoY Shift</span>
                      <span className={`text-[10.5px] font-bold ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                        {isUp ? '+' : ''}{detail.yoy_change}%
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Google Trends & VC Inflow Sidebar Right Panel */}
      <div className="flex flex-col gap-3">
        {/* Google Trends */}
        <div className="terminal-panel p-3">
          <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-2.5 flex items-center">
            <Search className="w-3.5 h-3.5 text-yellow-500 mr-1.5" />
            CITIZEN SENTIMENT: GOOGLE TRENDS QUERY INDEX
          </h3>
          <div className="space-y-2">
            {data && Object.entries(data.google_trends).map(([query, detail]) => {
              return (
                <div key={query} className="border-l-2 border-yellow-500/50 pl-2 text-[10px] space-y-0.5">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-gray-350 italic">"{query}"</span>
                    <span className="text-yellow-400">{detail.query_volume} vol</span>
                  </div>
                  <div className="flex justify-between text-[8.5px] text-gray-500 font-sans">
                    <span>Trend: {detail.weekly_trend}</span>
                    <span className="text-[8.5px] max-w-[75%] truncate">{detail.significance}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Venture Capital Index */}
        <div className="terminal-panel p-3 flex-1 flex flex-col justify-between min-h-[200px]">
          <div>
            <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1 flex items-center">
              <BarChart2 className="w-3.5 h-3.5 text-emerald-500 mr-1.5" />
              VENTURE CAPITAL STARTUP FUNDING INFLOW
            </h3>
            <span className="text-[8.5px] text-gray-500 block mb-1">
              Latest Month Influx: ${data?.startup_funding.latest_volume_usd_m}M across {data?.startup_funding.latest_deal_count} deals
            </span>
          </div>

          <div className="flex-1 min-h-[120px] border border-gray-900 bg-gray-950/40 rounded p-1 flex items-center justify-center">
            {renderFundingChart()}
          </div>
        </div>
      </div>
      
    </div>
  );
}

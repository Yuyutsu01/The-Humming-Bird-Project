'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Clock, Activity, BarChart2, DollarSign } from 'lucide-react';

interface TickerDetails {
  ticker: string;
  price: number;
  change_pct: number;
  timestamp: string;
}

interface MarketSnapshot {
  global_markets: Record<string, TickerDetails>;
  indian_markets: Record<string, TickerDetails>;
  commodities: Record<string, TickerDetails>;
  forex: Record<string, TickerDetails>;
  bonds: Record<string, TickerDetails>;
}

interface BarData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function InvestorDashboard({ liveTicks }: { liveTicks: any }) {
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<string>('Nifty 50');
  const [chartData, setChartData] = useState<BarData[]>([]);
  const [period, setPeriod] = useState<string>('1mo');
  const [loadingChart, setLoadingChart] = useState(false);

  // Correlation Matrix Data (Gold vs Dollar, Oil vs Inflation, etc.)
  const correlations = [
    { assetA: 'Gold', assetB: 'US Dollar (DXY)', value: -0.68, desc: 'Safe-haven hedge; rises when USD softens.' },
    { assetA: 'Crude Oil', assetB: 'India CPI Inflation', value: 0.82, desc: 'High correlation due to import reliance.' },
    { assetA: 'US 10Y Yield', assetB: 'FII Capital Flows', value: -0.74, desc: 'Rising yields prompt equity outflows.' },
    { assetA: 'USD/INR', assetB: 'IT Index', value: 0.61, desc: 'Weaker Rupee boosts exporter revenue.' },
    { assetA: 'RBI Repo Rate', assetB: 'Nifty 50 Index', value: -0.45, desc: 'High lending rates contract equity P/E.' }
  ];

  // Fetch initial snapshot
  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/market/snapshot');
        if (!resp.ok) throw new Error('API server error');
        const data = await resp.json();
        setSnapshot(data);
      } catch (e) {
        console.error("Failed to load market snapshot:", e);
      }
    };
    fetchSnapshot();
  }, []);

  // Fetch chart data when selected asset or period changes
  useEffect(() => {
    const fetchChart = async () => {
      setLoadingChart(true);
      try {
        const resp = await fetch(`http://localhost:8000/api/market/history?name=${encodeURIComponent(selectedAsset)}&period=${period}`);
        if (!resp.ok) throw new Error('API server error');
        const data = await resp.json();
        setChartData(data);
      } catch (e) {
        console.error("Failed to load historical chart:", e);
      } finally {
        setLoadingChart(false);
      }
    };
    fetchChart();
  }, [selectedAsset, period]);

  // Combine static snapshot with live WebSocket ticks
  const getDisplaySnapshot = () => {
    if (!snapshot) return null;
    if (!liveTicks || Object.keys(liveTicks).length === 0) return snapshot;

    const updated = JSON.parse(JSON.stringify(snapshot));
    // Apply updates
    for (const cat of Object.keys(updated)) {
      for (const name of Object.keys(updated[cat])) {
        if (liveTicks[name]) {
          updated[cat][name].price = liveTicks[name].price;
          updated[cat][name].change_pct = liveTicks[name].change_pct;
        }
      }
    }
    return updated;
  };

  const currentSnapshot = getDisplaySnapshot();

  // Rendering custom SVG Candlestick Chart
  const renderCandlestickChart = () => {
    if (loadingChart) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500 font-mono text-[10px]">
          Retrieving market records...
        </div>
      );
    }
    if (chartData.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500 font-mono text-[10px]">
          No data available for this asset.
        </div>
      );
    }

    // Chart dimensions
    const width = 650;
    const height = 240;
    const paddingLeft = 45;
    const paddingRight = 10;
    const paddingTop = 15;
    const paddingBottom = 25;

    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;

    // Find min and max prices
    const prices = chartData.flatMap(d => [d.high, d.low]);
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;

    // Add 5% buffer on top and bottom of chart
    const yMax = maxPrice + (priceRange * 0.05);
    const yMin = minPrice - (priceRange * 0.05);
    const yRange = yMax - yMin;

    const getX = (index: number) => paddingLeft + (index * (chartWidth / (chartData.length - 1)));
    const getY = (price: number) => paddingTop + chartHeight - (((price - yMin) / yRange) * chartHeight);

    return (
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${height}`}>
        {/* Horizontal grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
          const price = yMin + (yRange * ratio);
          const y = getY(price);
          return (
            <g key={idx}>
              <line x1={paddingLeft} y1={y} x2={width - paddingRight} y2={y} stroke="#1f2937" strokeWidth="0.5" strokeDasharray="2,2" />
              <text x={paddingLeft - 8} y={y + 3} textAnchor="end" fill="#6b7280" className="text-[9px] font-mono">
                {price < 10 ? price.toFixed(3) : Math.round(price).toLocaleString()}
              </text>
            </g>
          );
        })}

        {/* Date labels at bottom */}
        {chartData.map((d, idx) => {
          // Label every 5th or 6th date depending on length
          const divider = chartData.length > 30 ? 6 : 4;
          if (idx % divider === 0) {
            const x = getX(idx);
            return (
              <text key={idx} x={x} y={height - 8} textAnchor="middle" fill="#6b7280" className="text-[8px] font-mono">
                {d.date.substring(5)}
              </text>
            );
          }
          return null;
        })}

        {/* Draw candlesticks */}
        {chartData.map((d, idx) => {
          const x = getX(idx);
          const yOpen = getY(d.open);
          const yClose = getY(d.close);
          const yHigh = getY(d.high);
          const yLow = getY(d.low);

          const isBullish = d.close >= d.open;
          const strokeColor = isBullish ? '#10b981' : '#ef4444';
          const fillColor = isBullish ? '#10b981' : '#ef4444';
          const wickWidth = 1;
          const bodyWidth = Math.max(3, chartWidth / chartData.length * 0.7);

          return (
            <g key={idx}>
              {/* High-Low Wick line */}
              <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={strokeColor} strokeWidth={wickWidth} />
              {/* Open-Close Body Rect */}
              <rect
                x={x - bodyWidth / 2}
                y={Math.min(yOpen, yClose)}
                width={bodyWidth}
                height={Math.max(1.5, Math.abs(yOpen - yClose))}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth="0.5"
              />
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 h-full overflow-y-auto pr-1">
      {/* Tickers Snapshot Left Panel */}
      <div className="border border-gray-800 rounded bg-[#090d16]/30 p-2.5 flex flex-col gap-3 lg:col-span-1">
        <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1 flex items-center">
          <Clock className="w-3.5 h-3.5 text-blue-500 mr-1.5" />
          REAL-TIME STREAMING TIQUETS
        </h3>

        {currentSnapshot ? (
          <div className="space-y-3.5 flex-1 overflow-y-auto pr-1 max-h-[500px]">
            {/* Categorized groups */}
            {[
              { label: 'Indian Markets', key: 'indian_markets' },
              { label: 'Global Markets', key: 'global_markets' },
              { label: 'Commodities', key: 'commodities' },
              { label: 'Forex (USD/INR)', key: 'forex' }
            ].map(group => {
              const items = currentSnapshot[group.key as keyof MarketSnapshot];
              if (!items) return null;

              return (
                <div key={group.key} className="space-y-1.5">
                  <span className="text-[9px] text-gray-500 font-semibold uppercase tracking-wider block border-b border-gray-900 pb-0.5">
                    {group.label}
                  </span>
                  <div className="grid grid-cols-1 gap-1">
                    {Object.entries(items).map(([name, detail]) => {
                      const isUp = detail.change_pct >= 0;
                      const isSelected = selectedAsset === name;
                      return (
                        <div
                          key={name}
                          onClick={() => setSelectedAsset(name)}
                          className={`flex items-center justify-between p-1.5 rounded cursor-pointer transition-colors border ${
                            isSelected ? 'bg-blue-600/15 border-blue-500/50' : 'bg-gray-950/20 border-transparent hover:bg-gray-800/30'
                          }`}
                        >
                          <div className="flex flex-col">
                            <span className="text-[11px] font-bold text-gray-250 truncate max-w-[130px]">{name}</span>
                            <span className="text-[8px] text-gray-500">{detail.ticker}</span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-bold block text-gray-200">
                              {detail.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                            </span>
                            <span className={`text-[9px] font-bold flex items-center justify-end ${
                              isUp ? 'text-emerald-400' : 'text-red-400'
                            }`}>
                              {isUp ? <TrendingUp className="w-2.5 h-2.5 mr-0.5" /> : <TrendingDown className="w-2.5 h-2.5 mr-0.5" />}
                              {isUp ? '+' : ''}{detail.change_pct.toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-650">
            Connecting to tickers database...
          </div>
        )}
      </div>

      {/* Charts and Advanced Analytics Right Panels */}
      <div className="lg:col-span-2 flex flex-col gap-3">
        {/* Candlestick panel */}
        <div className="terminal-panel p-3 flex-1 flex flex-col min-h-[300px]">
          <div className="flex items-center justify-between border-b border-gray-850 pb-2 mb-2">
            <div className="flex flex-col">
              <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">CHARTS WINDOW</span>
              <span className="text-gray-150 font-bold text-xs uppercase">{selectedAsset} Historical Trend</span>
            </div>
            
            {/* Period select */}
            <div className="flex border border-gray-855 rounded overflow-hidden">
              {['1mo', '3mo'].map(p => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-2 py-0.5 text-[9px] uppercase transition-colors ${
                    period === p ? 'bg-blue-600/30 text-blue-300 font-bold' : 'text-gray-500 hover:text-gray-400'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 min-h-[200px] border border-gray-900/60 rounded bg-gray-950/20 p-2 flex items-center justify-center">
            {renderCandlestickChart()}
          </div>
        </div>

        {/* Correlation Engine Heatmap */}
        <div className="terminal-panel p-3">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-2.5 flex items-center">
            <Activity className="w-3.5 h-3.5 text-blue-500 mr-1.5" />
            CROSS-ASSET CAUSAL CORRELATION MATRIX
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-850 text-[9px] text-gray-500 uppercase">
                  <th className="py-1">Asset Variable A</th>
                  <th className="py-1">Macro Variable B</th>
                  <th className="py-1 text-center">Correlation Coefficient</th>
                  <th className="py-1">Transmission Narrative</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-900 text-[10px]">
                {correlations.map((row, idx) => {
                  const val = row.value;
                  const isPositive = val > 0;
                  const isHigh = Math.abs(val) > 0.6;
                  return (
                    <tr key={idx} className="hover:bg-gray-950/25">
                      <td className="py-2 text-gray-300 font-bold">{row.assetA}</td>
                      <td className="py-2 text-gray-300 font-bold">{row.assetB}</td>
                      <td className="py-2 text-center">
                        <span className={`px-2 py-0.5 rounded-sm font-bold ${
                          isPositive 
                            ? (isHigh ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-900/40' : 'bg-emerald-950/20 text-emerald-500')
                            : (isHigh ? 'bg-red-955/50 text-red-400 border border-red-900/40' : 'bg-red-955/20 text-red-500')
                        }`}>
                          {isPositive ? '+' : ''}{val.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-2 text-gray-500 leading-normal">{row.desc}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

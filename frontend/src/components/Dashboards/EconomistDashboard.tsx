'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, BarChart2, ShieldAlert, Cpu, Sparkles, TrendingUp, HelpCircle } from 'lucide-react';

interface IndicatorHistory {
  date: string;
  value: number;
}

interface IndicatorDetails {
  unit: string;
  current: number;
  description: string;
  source: string;
  frequency: string;
  history: IndicatorHistory[];
}

interface IndicatorsSnapshot {
  india: Record<string, IndicatorDetails>;
  global: Record<string, IndicatorDetails>;
}

interface ForecastPoint {
  date: string;
  value: number;
  upper_bound?: number;
  lower_bound?: number;
  type: 'Historical' | 'Actual' | 'Forecast';
}

interface ForecastResult {
  model: string;
  target: string;
  confidence_score: number;
  reasoning: string;
  key_drivers: string[];
  data: ForecastPoint[];
}

export default function EconomistDashboard() {
  const [indicators, setIndicators] = useState<IndicatorsSnapshot | null>(null);
  const [selectedIndRegion, setSelectedIndRegion] = useState<string>('india');
  const [selectedIndName, setSelectedIndName] = useState<string>('CPI Inflation');
  
  // Forecast states
  const [forecastModel, setForecastModel] = useState<string>('Prophet');
  const [forecastTarget, setForecastTarget] = useState<string>('CPI Inflation');
  const [forecastResult, setForecastResult] = useState<ForecastResult | null>(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  // Fetch all indicators on mount
  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/economy/indicators');
        if (!resp.ok) throw new Error('API server error');
        const data = await resp.json();
        setIndicators(data);
      } catch (e) {
        console.error("Failed to load indicators:", e);
      }
    };
    
    fetchIndicators();
  }, []);

  // Fetch forecast when model or target changes
  useEffect(() => {
    const fetchForecast = async () => {
      setLoadingForecast(true);
      try {
        const resp = await fetch(`http://localhost:8000/api/economy/forecast?model=${forecastModel}&target=${encodeURIComponent(forecastTarget)}`);
        if (!resp.ok) throw new Error('API server error');
        const data = await resp.json();
        setForecastResult(data);
      } catch (e) {
        console.error("Failed to load forecast:", e);
      } finally {
        setLoadingForecast(false);
      }
    };

    fetchForecast();
  }, [forecastModel, forecastTarget]);

  // Selected indicator details
  const currentIndicator = indicators?.[selectedIndRegion as keyof IndicatorsSnapshot]?.[selectedIndName];

  // Helper to draw SVG Historical Line Chart
  const renderIndicatorLineChart = () => {
    if (!currentIndicator) return null;
    const history = [...currentIndicator.history].reverse(); // Oldest to newest
    if (history.length === 0) return null;

    const width = 450;
    const height = 140;
    const paddingLeft = 30;
    const paddingRight = 10;
    const paddingTop = 10;
    const paddingBottom = 20;

    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;

    const values = history.map(h => h.value);
    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const range = maxVal - minVal;
    
    // Add 10% vertical buffer
    const yMax = maxVal + (range * 0.1 || 1);
    const yMin = minVal - (range * 0.1 || 1);
    const yRange = yMax - yMin;

    const getX = (index: number) => paddingLeft + (index * (chartWidth / (history.length - 1)));
    const getY = (val: number) => paddingTop + chartHeight - (((val - yMin) / yRange) * chartHeight);

    // Build SVG path
    let pathD = '';
    history.forEach((point, idx) => {
      const x = getX(idx);
      const y = getY(point.value);
      if (idx === 0) {
        pathD = `M ${x} ${y}`;
      } else {
        pathD += ` L ${x} ${y}`;
      }
    });

    return (
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${height}`}>
        {/* Grid lines */}
        {[0, 0.5, 1].map((ratio, idx) => {
          const val = yMin + (yRange * ratio);
          const y = getY(val);
          return (
            <g key={idx}>
              <line x1={paddingLeft} y1={y} x2={width - paddingRight} y2={y} stroke="#111827" strokeWidth="0.5" strokeDasharray="2,2" />
              <text x={paddingLeft - 5} y={y + 3} textAnchor="end" fill="#4b5563" className="text-[8px] font-mono">
                {val.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Date labels at bottom */}
        {history.map((h, idx) => {
          if (idx === 0 || idx === history.length - 1 || (idx === Math.floor(history.length / 2))) {
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
          fill="url(#gradient-area)"
        />

        {/* Main Line */}
        <path
          d={pathD}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="1.5"
        />

        {/* Nodes */}
        {history.map((h, idx) => {
          const x = getX(idx);
          const y = getY(h.value);
          const isLatest = idx === history.length - 1;
          return (
            <circle
              key={idx}
              cx={x}
              cy={y}
              r={isLatest ? 3.5 : 2}
              fill={isLatest ? '#3b82f6' : '#1e3a8a'}
              stroke={isLatest ? '#fff' : '#3b82f6'}
              strokeWidth={isLatest ? 1 : 0.5}
            />
          );
        })}

        {/* Gradients */}
        <defs>
          <linearGradient id="gradient-area" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.25"/>
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0"/>
          </linearGradient>
        </defs>
      </svg>
    );
  };

  // Helper to draw AI Forecast Chart with confidence bounds
  const renderForecastChart = () => {
    if (loadingForecast) {
      return (
        <div className="h-44 flex items-center justify-center text-gray-500 font-mono text-[9px]">
          Computing time-series forecast...
        </div>
      );
    }
    if (!forecastResult || forecastResult.data.length === 0) return null;

    const history = forecastResult.data;
    const width = 500;
    const height = 150;
    const paddingLeft = 35;
    const paddingRight = 10;
    const paddingTop = 10;
    const paddingBottom = 20;

    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;

    // Find min and max values including confidence upper/lower bounds
    const allVals = history.flatMap(d => [
      d.value, 
      d.upper_bound ?? d.value, 
      d.lower_bound ?? d.value
    ]);
    const maxVal = Math.max(...allVals);
    const minVal = Math.min(...allVals);
    const range = maxVal - minVal;
    
    const yMax = maxVal + (range * 0.08 || 1);
    const yMin = minVal - (range * 0.08 || 1);
    const yRange = yMax - yMin;

    const getX = (index: number) => paddingLeft + (index * (chartWidth / (history.length - 1)));
    const getY = (val: number) => paddingTop + chartHeight - (((val - yMin) / yRange) * chartHeight);

    // Build paths: Historical Line vs Forecast Line vs Shaded Confidence Interval
    let histPathD = '';
    let forePathD = '';
    let upperPathD = '';
    let lowerPathD = '';

    const histPoints = history.filter(d => d.type === 'Historical' || d.type === 'Actual');
    const forePoints = history.filter(d => d.type === 'Actual' || d.type === 'Forecast');

    histPoints.forEach((d, idx) => {
      const origIdx = history.findIndex(p => p.date === d.date);
      const x = getX(origIdx);
      const y = getY(d.value);
      if (idx === 0) histPathD = `M ${x} ${y}`;
      else histPathD += ` L ${x} ${y}`;
    });

    forePoints.forEach((d, idx) => {
      const origIdx = history.findIndex(p => p.date === d.date);
      const x = getX(origIdx);
      const y = getY(d.value);
      if (idx === 0) forePathD = `M ${x} ${y}`;
      else forePathD += ` L ${x} ${y}`;
    });

    // Build shaded bounds path
    // Forward along upper bound, backward along lower bound
    const foreOnly = history.filter(d => d.type === 'Forecast');
    if (foreOnly.length > 0) {
      // Find starting point (Actual)
      const actualPt = history.find(d => d.type === 'Actual');
      const startIdx = actualPt ? history.findIndex(p => p.date === actualPt.date) : history.length - foreOnly.length - 1;
      const startX = getX(startIdx);
      const startY = getY(actualPt?.value || foreOnly[0].value);

      upperPathD = `M ${startX} ${startY}`;
      foreOnly.forEach((d) => {
        const origIdx = history.findIndex(p => p.date === d.date);
        upperPathD += ` L ${getX(origIdx)} ${getY(d.upper_bound ?? d.value)}`;
      });

      lowerPathD = `L ${getX(history.length - 1)} ${getY(foreOnly[foreOnly.length - 1].lower_bound ?? foreOnly[foreOnly.length - 1].value)}`;
      for (let i = foreOnly.length - 2; i >= 0; i--) {
        const origIdx = history.findIndex(p => p.date === foreOnly[i].date);
        lowerPathD += ` L ${getX(origIdx)} ${getY(foreOnly[i].lower_bound ?? foreOnly[i].value)}`;
      }
      lowerPathD += ` L ${startX} ${startY} Z`;
    }

    return (
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${height}`}>
        {/* Horizontal grids */}
        {[0, 0.5, 1].map((ratio, idx) => {
          const val = yMin + (yRange * ratio);
          const y = getY(val);
          return (
            <g key={idx}>
              <line x1={paddingLeft} y1={y} x2={width - paddingRight} y2={y} stroke="#111827" strokeWidth="0.5" strokeDasharray="2,2" />
              <text x={paddingLeft - 5} y={y + 3} textAnchor="end" fill="#4b5563" className="text-[8px] font-mono">
                {val.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Date labels at bottom */}
        {history.map((h, idx) => {
          if (idx === 0 || idx === histPoints.length - 1 || idx === history.length - 1) {
            const x = getX(idx);
            return (
              <text key={idx} x={x} y={height - 4} textAnchor="middle" fill="#4b5563" className="text-[7.5px] font-mono">
                {h.date}
              </text>
            );
          }
          return null;
        })}

        {/* Confidence Shading Area */}
        {upperPathD && lowerPathD && (
          <path
            d={`${upperPathD} ${lowerPathD}`}
            fill="#3b82f6"
            fillOpacity="0.08"
            stroke="rgba(59, 130, 246, 0.15)"
            strokeWidth="0.5"
            strokeDasharray="2,2"
          />
        )}

        {/* Historical line segment */}
        {histPathD && (
          <path
            d={histPathD}
            fill="none"
            stroke="#6b7280"
            strokeWidth="1.2"
          />
        )}

        {/* Forecasted line segment (dotted/blue) */}
        {forePathD && (
          <path
            d={forePathD}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="1.5"
            strokeDasharray="3,3"
          />
        )}

        {/* Actual transition node */}
        {histPoints.length > 0 && (
          <circle
            cx={getX(histPoints.length - 1)}
            cy={getY(histPoints[histPoints.length - 1].value)}
            r={3}
            fill="#3b82f6"
            stroke="#fff"
            strokeWidth="0.5"
          />
        )}
      </svg>
    );
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 h-full overflow-y-auto pr-1">
      {/* Macro Indicators List Left Panel */}
      <div className="border border-gray-800 rounded bg-[#090d16]/30 p-2.5 flex flex-col gap-2.5 xl:col-span-1 min-h-[300px]">
        <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1 flex items-center">
          <TrendingUp className="w-3.5 h-3.5 text-blue-500 mr-1.5" />
          NATIONAL ECONOMIC INDICATORS HUB
        </h3>

        {/* Region tabs */}
        <div className="flex border border-gray-900 rounded overflow-hidden mb-1">
          {['india', 'global'].map(r => (
            <button
              key={r}
              onClick={() => {
                setSelectedIndRegion(r);
                // Switch default selected name
                setSelectedIndName(r === 'india' ? 'CPI Inflation' : 'Federal Reserve Rates');
              }}
              className={`flex-1 py-1 text-[9px] uppercase transition-colors font-bold ${
                selectedIndRegion === r ? 'bg-blue-600/20 text-blue-300' : 'text-gray-500 hover:text-gray-400'
              }`}
            >
              {r === 'india' ? 'India' : 'Global'}
            </button>
          ))}
        </div>

        {indicators ? (
          <div className="space-y-1.5 flex-1 overflow-y-auto pr-1 max-h-[220px] xl:max-h-[300px]">
            {Object.entries(indicators[selectedIndRegion as keyof IndicatorsSnapshot] || {}).map(([name, detail]) => {
              const isSelected = selectedIndName === name;
              return (
                <div
                  key={name}
                  onClick={() => setSelectedIndName(name)}
                  className={`flex flex-col p-1.5 rounded cursor-pointer transition-colors border ${
                    isSelected ? 'bg-blue-600/15 border-blue-500/50' : 'bg-gray-950/20 border-transparent hover:bg-gray-800/30'
                  }`}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-[11px] text-gray-250 truncate max-w-[170px]">{name}</span>
                    <span className="text-xs font-bold text-gray-150">
                      {detail.current}
                      <span className="text-[9px] text-gray-500 font-normal ml-0.5">{detail.unit}</span>
                    </span>
                  </div>
                  <span className="text-[8px] text-gray-500 font-sans truncate">{detail.description}</span>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-650">
            Querying macroeconomic indexes...
          </div>
        )}

        {/* Mini historical panel inside left tab */}
        {currentIndicator && (
          <div className="border-t border-gray-900 pt-2 flex-1 flex flex-col justify-end">
            <span className="text-[9px] text-gray-500 font-semibold uppercase mb-1 block">
              {selectedIndName} Historical Series (Source: {currentIndicator.source})
            </span>
            <div className="h-28 border border-gray-900 bg-gray-950/40 rounded p-1 flex items-center justify-center">
              {renderIndicatorLineChart()}
            </div>
          </div>
        )}
      </div>

      {/* AI Forecasting Dashboard Right Panels */}
      <div className="xl:col-span-2 flex flex-col gap-3">
        <div className="terminal-panel p-3 flex-1 flex flex-col min-h-[350px]">
          {/* Header select */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-850 pb-2.5 mb-3 gap-2">
            <div className="flex items-center">
              <Sparkles className="w-4 h-4 text-blue-400 mr-1.5 animate-pulse" />
              <span className="font-bold text-gray-200 uppercase tracking-wider">AI TIME-SERIES FORECASTING SERVICE</span>
            </div>
            
            {/* Controls */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <span className="text-[9px] text-gray-500">Model:</span>
                <select
                  value={forecastModel}
                  onChange={(e) => setForecastModel(e.target.value)}
                  className="bg-gray-950 border border-gray-800 rounded px-1.5 py-0.5 text-[9px] text-gray-300 outline-none"
                >
                  {['Prophet', 'XGBoost', 'LSTM', 'Temporal Fusion Transformer'].map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-1">
                <span className="text-[9px] text-gray-500">Variable:</span>
                <select
                  value={forecastTarget}
                  onChange={(e) => setForecastTarget(e.target.value)}
                  className="bg-gray-950 border border-gray-800 rounded px-1.5 py-0.5 text-[9px] text-gray-300 outline-none"
                >
                  {['CPI Inflation', 'Oil Prices', 'Gold Prices', 'USD/INR', 'GDP Growth'].map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Core visual forecast */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 flex-1">
            {/* Left Model Details & Explainable AI */}
            <div className="md:col-span-1 border border-gray-850 bg-gray-950/20 rounded p-2.5 flex flex-col justify-between">
              <div>
                <span className="text-[9px] text-gray-500 font-bold block mb-1">MODEL SPECIFICATION:</span>
                <p className="text-[10px] text-gray-400 leading-normal mb-2">
                  {forecastResult?.model === 'Prophet' && 'Prophet combines trend regressions with seasonal Fourier terms. High stability, excellent for long-term policy modeling.'}
                  {forecastResult?.model === 'XGBoost' && 'XGBoost extracts decision tree combinations from lagged economic parameters. Sensitive to recent volatility jumps.'}
                  {forecastResult?.model === 'LSTM' && 'LSTM recurrent cells recall memory sequences. Captures complex wave dynamics and short-term trends.'}
                  {forecastResult?.model === 'Temporal Fusion Transformer' && 'TFT utilizes self-attention weighting vectors. Excels at cross-variable economic causality prediction.'}
                </p>
                
                <span className="text-[9px] text-gray-500 font-bold block mb-1">EXPLAINABLE AI REASONING:</span>
                <p className="text-[10px] text-gray-350 leading-relaxed italic">
                  "{forecastResult?.reasoning}"
                </p>
              </div>

              <div className="mt-3 border-t border-gray-900 pt-2">
                <div className="flex items-center justify-between text-[10px] mb-1">
                  <span className="text-gray-500">Confidence Score:</span>
                  <span className="text-blue-300 font-bold">{forecastResult?.confidence_score}%</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full" style={{ width: `${forecastResult?.confidence_score}%` }} />
                </div>
              </div>
            </div>

            {/* Right Chart Visualization & Drivers */}
            <div className="md:col-span-2 flex flex-col justify-between gap-3">
              {/* Forecast chart container */}
              <div className="flex-1 min-h-[160px] border border-gray-900 bg-gray-950/40 rounded p-2 flex items-center justify-center">
                {renderForecastChart()}
              </div>

              {/* Forecast drivers footer */}
              {forecastResult && (
                <div className="border border-gray-850 bg-gray-900/10 rounded p-2 flex items-center justify-between">
                  <div className="flex items-center text-[10px] text-gray-500">
                    <Cpu className="w-3.5 h-3.5 text-blue-500 mr-1.5" />
                    <span>Forecast Key Drivers:</span>
                  </div>
                  <div className="flex gap-2">
                    {forecastResult.key_drivers.map((drv, i) => (
                      <span key={i} className="px-2 py-0.5 rounded-sm bg-gray-800/80 border border-gray-800 text-[9px] text-gray-300 font-bold uppercase tracking-tight">
                        {drv}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

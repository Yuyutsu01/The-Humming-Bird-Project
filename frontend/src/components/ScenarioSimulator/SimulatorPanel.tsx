'use client';

import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw, BarChart2, ShieldAlert, Cpu, Percent } from 'lucide-react';

interface SimulationMetric {
  value: number;
  baseline: number;
  change: number;
  change_pct?: number;
  status: string;
}

interface SectorImpact {
  name: string;
  score: number;
  impact: string;
  driver: string;
}

interface SimulationResult {
  inputs: {
    oil_price: float;
    fed_rate: float;
    geopolitical_risk: float;
  };
  metrics: {
    usd_inr: SimulationMetric;
    cpi_inflation: SimulationMetric;
    rbi_repo_rate: SimulationMetric;
    gdp_growth: SimulationMetric;
    nifty_50: SimulationMetric;
  };
  sectors: SectorImpact[];
}

export default function SimulatorPanel() {
  const [oilPrice, setOilPrice] = useState(82.5);
  const [fedRate, setFedRate] = useState(5.25);
  const [geoRisk, setGeoRisk] = useState(40.0);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSimulation = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`http://localhost:8000/api/scenario/simulate?oil_price=${oilPrice}&fed_rate=${fedRate}&geopolitical_risk=${geoRisk}`);
      if (!resp.ok) throw new Error('API server error');
      const data = await resp.json();
      setResult(data);
    } catch (e) {
      console.error("Failed to fetch simulation result: ", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Run simulation when sliders change (debounced slightly to prevent API overload)
    const delay = setTimeout(() => {
      fetchSimulation();
    }, 200);
    return () => clearTimeout(delay);
  }, [oilPrice, fedRate, geoRisk]);

  const resetSliders = () => {
    setOilPrice(82.5);
    setFedRate(5.25);
    setGeoRisk(40.0);
  };

  return (
    <div className="terminal-panel p-4 h-full flex flex-col font-mono text-xs overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-2 mb-3">
        <div className="flex items-center text-gray-250">
          <Sliders className="w-4 h-4 text-emerald-500 mr-2" />
          <span className="font-bold">GLOBAL ECONOMIC SCENARIO SIMULATOR</span>
        </div>
        <button 
          onClick={resetSliders}
          className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Reset Baseline
        </button>
      </div>

      {/* Simulator Grid */}
      <div className="flex flex-row gap-4 flex-1">
        {/* Sliders Control Column */}
        <div className="border border-gray-800 rounded bg-[#090d16]/30 p-3 flex flex-col justify-around gap-4 w-[220px] shrink-0">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1">
            Input Global Shocks
          </h4>
          
          {/* Slider 1: Brent Crude */}
          <div className="space-y-1">
            <div className="flex justify-between font-bold text-gray-200">
              <span>Crude Oil (Brent)</span>
              <span className="text-emerald-400">${oilPrice.toFixed(1)} / bbl</span>
            </div>
            <input 
              type="range" 
              min="40" 
              max="200" 
              step="0.5"
              value={oilPrice} 
              onChange={(e) => setOilPrice(parseFloat(e.target.value))}
              className="w-full accent-emerald-500 cursor-ew-resize bg-gray-900 h-1.5 rounded"
            />
            <div className="flex justify-between text-[9px] text-gray-650">
              <span>$40 (Recession)</span>
              <span>$82.5 (Base)</span>
              <span>$200 (Energy Crisis)</span>
            </div>
          </div>

          {/* Slider 2: Fed Rate */}
          <div className="space-y-1">
            <div className="flex justify-between font-bold text-gray-200">
              <span>US Fed Rate</span>
              <span className="text-blue-400">{fedRate.toFixed(2)}%</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="10" 
              step="0.25"
              value={fedRate} 
              onChange={(e) => setFedRate(parseFloat(e.target.value))}
              className="w-full accent-blue-500 cursor-ew-resize bg-gray-900 h-1.5 rounded"
            />
            <div className="flex justify-between text-[9px] text-gray-650">
              <span>0.0% (ZIRP)</span>
              <span>5.25% (Base)</span>
              <span>10.0% (Hyper-tight)</span>
            </div>
          </div>

          {/* Slider 3: Geopolitical Risk */}
          <div className="space-y-1">
            <div className="flex justify-between font-bold text-gray-200">
              <span>Geopolitical Risk</span>
              <span className="text-red-400">{geoRisk.toFixed(0)} / 100</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="100" 
              step="1"
              value={geoRisk} 
              onChange={(e) => setGeoRisk(parseFloat(e.target.value))}
              className="w-full accent-red-500 cursor-ew-resize bg-gray-900 h-1.5 rounded"
            />
            <div className="flex justify-between text-[9px] text-gray-650">
              <span>0 (Global Peace)</span>
              <span>40 (Base)</span>
              <span>100 (Global Conflict)</span>
            </div>
          </div>
        </div>

        {/* Metrics Output Column */}
        <div className="flex-1 flex flex-col gap-3 justify-between">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">
            Simulated Domestic Macro Targets
          </h4>

          {result ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 flex-1">
              {/* Card 1: USD/INR */}
              <div className="border border-gray-800/80 bg-gray-900/10 rounded p-2.5 flex flex-col justify-between">
                <span className="text-[9px] text-gray-500 block font-semibold uppercase">Exchange Rate</span>
                <span className="text-gray-150 font-bold text-lg block my-1">
                  ₹{result.metrics.usd_inr.value.toFixed(2)}
                </span>
                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-bold ${result.metrics.usd_inr.change > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {result.metrics.usd_inr.change > 0 ? '+' : ''}{result.metrics.usd_inr.change.toFixed(2)} ({result.metrics.usd_inr.change_pct}%)
                  </span>
                  <span className="text-gray-600 block text-[9px]">{result.metrics.usd_inr.status}</span>
                </div>
              </div>

              {/* Card 2: CPI Inflation */}
              <div className="border border-gray-800/80 bg-gray-900/10 rounded p-2.5 flex flex-col justify-between">
                <span className="text-[9px] text-gray-500 block font-semibold uppercase">CPI Inflation</span>
                <span className="text-gray-150 font-bold text-lg block my-1">
                  {result.metrics.cpi_inflation.value.toFixed(2)}%
                </span>
                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-bold ${result.metrics.cpi_inflation.change > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {result.metrics.cpi_inflation.change > 0 ? '+' : ''}{result.metrics.cpi_inflation.change.toFixed(2)}%
                  </span>
                  <span className="text-gray-600 block text-[9px]">{result.metrics.cpi_inflation.status}</span>
                </div>
              </div>

              {/* Card 3: RBI Repo Rate */}
              <div className="border border-gray-800/80 bg-gray-900/10 rounded p-2.5 flex flex-col justify-between">
                <span className="text-[9px] text-gray-500 block font-semibold uppercase">RBI Repo Rate</span>
                <span className="text-gray-150 font-bold text-lg block my-1">
                  {result.metrics.rbi_repo_rate.value.toFixed(2)}%
                </span>
                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-bold ${result.metrics.rbi_repo_rate.change > 0 ? 'text-red-400' : (result.metrics.rbi_repo_rate.change < 0 ? 'text-emerald-400' : 'text-gray-500')}`}>
                    {result.metrics.rbi_repo_rate.change > 0 ? '+' : ''}{result.metrics.rbi_repo_rate.change.toFixed(2)}%
                  </span>
                  <span className="text-gray-600 block text-[9px]">{result.metrics.rbi_repo_rate.status}</span>
                </div>
              </div>

              {/* Card 4: GDP Growth */}
              <div className="border border-gray-800/80 bg-gray-900/10 rounded p-2.5 flex flex-col justify-between">
                <span className="text-[9px] text-gray-500 block font-semibold uppercase">GDP Growth</span>
                <span className="text-gray-150 font-bold text-lg block my-1">
                  {result.metrics.gdp_growth.value.toFixed(2)}%
                </span>
                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-bold ${result.metrics.gdp_growth.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {result.metrics.gdp_growth.change > 0 ? '+' : ''}{result.metrics.gdp_growth.change.toFixed(2)}%
                  </span>
                  <span className="text-gray-600 block text-[9px]">{result.metrics.gdp_growth.status}</span>
                </div>
              </div>

              {/* Card 5: Nifty 50 */}
              <div className="border border-gray-800/80 bg-gray-900/10 rounded p-2.5 flex flex-col justify-between col-span-2">
                <span className="text-[9px] text-gray-500 block font-semibold uppercase">Indian Equities (Nifty 50)</span>
                <span className="text-gray-150 font-bold text-lg block my-1">
                  {result.metrics.nifty_50.value.toLocaleString()}
                </span>
                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-bold ${result.metrics.nifty_50.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {result.metrics.nifty_50.change > 0 ? '+' : ''}{result.metrics.nifty_50.change.toLocaleString()} ({result.metrics.nifty_50.change_pct}%)
                  </span>
                  <span className="text-gray-600 block text-[9px]">{result.metrics.nifty_50.status}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-600">
              Running simulation projections...
            </div>
          )}
        </div>
      </div>

      {/* Sector Impact Heatmap */}
      {result && (
        <div className="mt-3 border border-gray-850 bg-gray-950/20 rounded p-2.5">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-2 flex items-center">
            <Cpu className="w-3.5 h-3.5 text-blue-500 mr-1" />
            Sector Sensitivity Index
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {result.sectors.map((sec) => {
              const isPositive = sec.score > 0;
              const isNegative = sec.score < 0;
              const absScore = Math.abs(sec.score);
              
              let barColor = 'bg-gray-700';
              let textGlow = 'text-gray-400';
              if (isPositive) {
                barColor = 'bg-emerald-500';
                textGlow = 'text-emerald-400';
              } else if (isNegative) {
                barColor = 'bg-red-500';
                textGlow = 'text-red-400';
              }

              return (
                <div key={sec.name} className="border border-gray-800 bg-[#070b13]/50 p-2 rounded flex flex-col justify-between">
                  <div className="flex justify-between font-bold leading-tight mb-1">
                    <span className="text-[9px] text-gray-300 truncate max-w-[75%]">{sec.name}</span>
                    <span className={`text-[10px] font-bold ${textGlow}`}>
                      {isPositive ? '+' : ''}{sec.score}
                    </span>
                  </div>
                  {/* Progress bar visual */}
                  <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden flex">
                    {/* Left negative bar or right positive bar */}
                    {isNegative ? (
                      <div className="flex-1 flex justify-end">
                        <div className="h-full bg-red-500" style={{ width: `${Math.min(100, absScore * 1.5)}%` }} />
                      </div>
                    ) : (
                      <div className="flex-1 flex justify-start">
                        <div className="h-full bg-emerald-500" style={{ width: `${Math.min(100, absScore * 1.5)}%` }} />
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between text-[8px] text-gray-600 mt-1 font-sans">
                    <span>{sec.impact}</span>
                    <span className="truncate max-w-[75%]">{sec.driver}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

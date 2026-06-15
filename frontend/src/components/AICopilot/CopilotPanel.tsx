'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Cpu, ChevronDown, ChevronUp, AlertCircle, FileText, TrendingUp, Sparkles, BookOpen } from 'lucide-react';

interface AIResult {
  engine: string;
  query: string;
  title: string;
  summary: string;
  cause: string;
  effect: string;
  india_impact: string[];
  details: {
    root_cause: string;
    risks: string;
    opportunities: string;
    historical_comparison: string;
    predictions: string;
  };
}

interface CopilotPanelProps {
  onSearchQuery?: string;
  onNavigateToDashboard?: (dbName: string) => void;
}

export default function CopilotPanel({ onSearchQuery, onNavigateToDashboard }: CopilotPanelProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Array<{ type: 'user' | 'bot'; text?: string; result?: AIResult }>>([
    {
      type: 'bot',
      text: 'Welcome to AI Economic Copilot. Ask any question regarding how global market shifts or conflicts propagate to India (e.g. "Why is gold rising?", "What sectors benefit from a weaker rupee?").'
    }
  ]);
  const [expandedDetails, setExpandedDetails] = useState<Record<number, boolean>>({});
  const [activeTab, setActiveTab] = useState<Record<number, string>>({});

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  // Handle queries passed from the outer layout (e.g. CommandBar search or quick links)
  useEffect(() => {
    if (onSearchQuery) {
      handleSearch(onSearchQuery);
    }
  }, [onSearchQuery]);

  const handleSearch = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    setHistory(prev => [...prev, { type: 'user', text }]);
    setQuery('');

    try {
      const resp = await fetch(`http://localhost:8000/api/ai/ask?query=${encodeURIComponent(text)}`);
      if (!resp.ok) throw new Error('API server error');
      const data: AIResult = await resp.json();
      
      setHistory(prev => [...prev, { type: 'bot', result: data }]);
      const idx = history.length + 1;
      setExpandedDetails(prev => ({ ...prev, [idx]: true }));
      setActiveTab(prev => ({ ...prev, [idx]: 'root' }));
    } catch (e) {
      setHistory(prev => [
        ...prev, 
        { 
          type: 'bot', 
          text: 'Error connecting to the economic intelligence backend. Please ensure the FastAPI server is running on http://localhost:8000.' 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleDetails = (idx: number) => {
    setExpandedDetails(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleTabChange = (idx: number, tabName: string) => {
    setActiveTab(prev => ({ ...prev, [idx]: tabName }));
  };

  return (
    <div className="flex flex-col h-full bg-[#070b13] border-l border-gray-800 font-mono">
      {/* Header */}
      <div className="flex items-center px-4 py-3 border-b border-gray-800 bg-[#090d16]/80 backdrop-blur-sm">
        <Sparkles className="w-4 h-4 text-blue-400 mr-2 animate-pulse" />
        <h2 className="text-xs font-bold text-gray-200 tracking-wider">AI CO-PILOT RESEARCH ANALYST</h2>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {history.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] rounded p-3 text-xs ${
              msg.type === 'user' 
                ? 'bg-blue-600/20 border border-blue-600/40 text-blue-200 font-semibold' 
                : 'bg-gray-900/50 border border-gray-800 text-gray-300'
            }`}>
              {/* Bot Text Message */}
              {msg.text && <p className="leading-relaxed">{msg.text}</p>}

              {/* Bot Structured Report Result */}
              {msg.result && (
                <div className="space-y-3">
                  {/* Title and Engine Tag */}
                  <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                    <span className="font-bold text-blue-300 text-sm">{msg.result.title}</span>
                    <span className="text-[9px] px-1.5 py-0.2 bg-gray-800 rounded text-gray-500 font-mono">
                      {msg.result.engine}
                    </span>
                  </div>

                  {/* Summary */}
                  <div>
                    <span className="text-[10px] text-blue-400 font-bold block mb-1">EXECUTIVE SUMMARY:</span>
                    <p className="text-gray-300 text-xs leading-relaxed">{msg.result.summary}</p>
                  </div>

                  {/* Cause/Effect Grid */}
                  <div className="grid grid-cols-2 gap-2 border border-gray-800/80 rounded p-2 bg-[#090d16]/50">
                    <div>
                      <span className="text-[9px] text-gray-500 block uppercase">Root Trigger</span>
                      <span className="text-xs text-red-400 font-semibold">{msg.result.cause}</span>
                    </div>
                    <div>
                      <span className="text-[9px] text-gray-500 block uppercase">Direct Consequence</span>
                      <span className="text-xs text-yellow-400 font-semibold">{msg.result.effect}</span>
                    </div>
                  </div>

                  {/* India Impact Engine bullet list */}
                  <div className="border border-emerald-900/30 rounded p-2 bg-emerald-950/5">
                    <span className="text-[10px] text-emerald-400 font-bold block mb-1.5 flex items-center">
                      <Cpu className="w-3.5 h-3.5 mr-1" />
                      INDIA IMPACT ENGINE TRANSMISSION:
                    </span>
                    <ul className="space-y-1.5 list-none">
                      {msg.result.india_impact.map((imp, i) => (
                        <li key={i} className="text-gray-300 pl-3 relative text-[11px] leading-relaxed">
                          <span className="absolute left-0 top-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                          {imp}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Expandable Deep Research Report */}
                  <div className="border border-gray-800 rounded overflow-hidden">
                    <button 
                      onClick={() => toggleDetails(idx)}
                      className="w-full flex items-center justify-between px-2.5 py-1.5 bg-gray-900/40 text-[10px] text-gray-400 hover:text-gray-200"
                    >
                      <span className="font-bold flex items-center">
                        <FileText className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
                        DEEP RESEARCH & FORECASTING REPORT
                      </span>
                      {expandedDetails[idx] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {expandedDetails[idx] && (
                      <div className="p-2.5 bg-[#05070d] border-t border-gray-800 text-[11px]">
                        {/* Tab header */}
                        <div className="flex border-b border-gray-800 pb-1.5 mb-2 gap-1 overflow-x-auto">
                          {[
                            { id: 'root', label: 'Causality' },
                            { id: 'risks', label: 'Risks' },
                            { id: 'opps', label: 'Opps' },
                            { id: 'hist', label: 'History' },
                            { id: 'pred', label: 'Forecast' }
                          ].map(t => (
                            <button
                              key={t.id}
                              onClick={() => handleTabChange(idx, t.id)}
                              className={`px-1.5 py-0.5 rounded-sm text-[10px] transition-colors ${
                                activeTab[idx] === t.id ? 'bg-blue-600/30 text-blue-300 font-bold' : 'text-gray-500 hover:text-gray-400'
                              }`}
                            >
                              {t.label}
                            </button>
                          ))}
                        </div>

                        {/* Tab content */}
                        <div className="text-gray-400 leading-relaxed min-h-[60px]">
                          {activeTab[idx] === 'root' && msg.result.details.root_cause}
                          {activeTab[idx] === 'risks' && msg.result.details.risks}
                          {activeTab[idx] === 'opps' && msg.result.details.opportunities}
                          {activeTab[idx] === 'hist' && msg.result.details.historical_comparison}
                          {activeTab[idx] === 'pred' && msg.result.details.predictions}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-900/50 border border-gray-800 text-gray-400 rounded p-3 text-xs flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-blue-400 animate-spin" />
              <span>Analyzing macro transmission signals...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input area */}
      <form 
        onSubmit={(e) => {
          e.preventDefault();
          handleSearch(query);
        }}
        className="p-3 border-t border-gray-800 bg-[#090d16]/80 backdrop-blur-sm flex items-center"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask AI Analyst (e.g. Why is gold rising?)..."
          className="flex-1 h-9 bg-gray-950 border border-gray-800 rounded px-3 text-xs text-gray-200 outline-none focus:border-blue-600 font-mono"
        />
        <button
          type="submit"
          className="ml-2 w-9 h-9 flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

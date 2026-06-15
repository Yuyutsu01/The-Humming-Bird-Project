'use client';

import React, { useState, useEffect } from 'react';
import { Network, ArrowRight, HelpCircle, Cpu } from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  category: string;
  description: string;
  // Visual positions on SVG canvas
  x: number;
  y: number;
}

interface GraphLink {
  source: string;
  target: string;
  relationship: string;
  sign: string;
}

interface CausalityStep {
  step: number;
  source: string;
  target: string;
  relationship: string;
  sign: string;
}

export default function MacroGraph() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [links, setLinks] = useState<GraphLink[]>([]);
  
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [sourceNodeId, setSourceNodeId] = useState<string>('oil');
  const [targetNodeId, setTargetNodeId] = useState<string>('stock_market');
  const [causalityChain, setCausalityChain] = useState<CausalityStep[]>([]);
  const [loadingCausality, setLoadingCausality] = useState(false);

  // Load knowledge graph definition
  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/ai/relationship/graph');
        if (!resp.ok) throw new Error('API server error');
        const data = await resp.json();
        
        // Define clean visual coordinates for the nodes flow (Global -> Local -> Markets)
        const coords: Record<string, { x: number; y: number }> = {
          "us_bond_yields":     { x: 50,  y: 60 },
          "usd_strength":       { x: 50,  y: 180 },
          "oil":                { x: 50,  y: 300 },
          
          "fii_flow":           { x: 220, y: 60 },
          "usd_inr":            { x: 220, y: 200 },
          
          "inflation":          { x: 390, y: 260 },
          
          "rbi_rates":          { x: 560, y: 120 },
          "borrowing_cost":     { x: 720, y: 120 },
          "consumer_spending":  { x: 560, y: 320 },
          
          "corp_earnings":      { x: 860, y: 260 },
          "stock_market":       { x: 970, y: 190 }
        };

        const positionedNodes = data.nodes.map((n: any) => ({
          ...n,
          x: coords[n.id]?.x || 100,
          y: coords[n.id]?.y || 100
        }));

        setNodes(positionedNodes);
        setLinks(data.links);
        
        // Set initial selected node
        const oilNode = positionedNodes.find((n: any) => n.id === 'oil');
        if (oilNode) setSelectedNode(oilNode);
      } catch (e) {
        console.error("Failed to load knowledge graph: ", e);
      }
    };
    
    fetchGraph();
  }, []);

  // Compute causality when source or target changes
  useEffect(() => {
    const traceCausality = async () => {
      if (!sourceNodeId || !targetNodeId) return;
      setLoadingCausality(true);
      try {
        const resp = await fetch(`http://localhost:8000/api/ai/relationship/causality?source=${sourceNodeId}&target=${targetNodeId}`);
        if (!resp.ok) throw new Error('Causality API error');
        const data = await resp.json();
        
        if (Array.isArray(data)) {
          setCausalityChain(data);
        } else {
          setCausalityChain([]);
        }
      } catch (e) {
        console.error("Failed to trace causality: ", e);
      } finally {
        setLoadingCausality(false);
      }
    };

    traceCausality();
  }, [sourceNodeId, targetNodeId, nodes]);

  // Check if a link is part of the active causality path
  const isLinkInCausality = (link: GraphLink) => {
    return causalityChain.some(step => {
      const srcNode = nodes.find(n => n.label === step.source);
      const destNode = nodes.find(n => n.label === step.target);
      return srcNode?.id === link.source && destNode?.id === link.target;
    });
  };

  return (
    <div className="terminal-panel p-4 h-full flex flex-col font-mono text-xs overflow-y-auto">
      {/* Title */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-2 mb-3">
        <div className="flex items-center text-gray-200">
          <Network className="w-4 h-4 text-blue-500 mr-2" />
          <span className="font-bold">MACRO RELATIONSHIP GRAPH ENGINE</span>
        </div>
        <div className="text-[10px] text-gray-500">
          Interactive Knowledge Graph mapping causal flow
        </div>
      </div>

      {/* SVG Canvas Workspace */}
      <div className="flex-1 min-h-[350px] relative border border-gray-850/60 rounded bg-gray-950/40 p-2 overflow-x-auto">
        {nodes.length > 0 ? (
          <svg className="w-full h-full min-w-[1000px]" viewBox="0 0 1050 400">
            {/* Definitions of Markers for Arrows */}
            <defs>
              <marker id="arrow-positive" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
              <marker id="arrow-negative" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
              </marker>
              <marker id="arrow-neutral" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563" />
              </marker>
              <marker id="arrow-active" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
            </defs>

            {/* Draw Links/Edges */}
            {links.map((link, idx) => {
              const src = nodes.find(n => n.id === link.source);
              const dest = nodes.find(n => n.id === link.target);
              if (!src || !dest) return null;

              const active = isLinkInCausality(link);
              const signColor = link.sign === '+' ? '#10b981' : (link.sign === '-' ? '#ef4444' : '#4b5563');
              const lineColor = active ? '#3b82f6' : 'rgba(75, 85, 99, 0.2)';
              const strokeWidth = active ? '2.5' : '1.2';
              const marker = active ? 'url(#arrow-active)' : (link.sign === '+' ? 'url(#arrow-positive)' : 'url(#arrow-negative)');

              // Add a slight arc curve to prevent overlapping lines
              const dx = dest.x - src.x;
              const dy = dest.y - src.y;
              const dr = Math.sqrt(dx * dx + dy * dy);
              const isCurved = (link.source === 'oil' && link.target === 'corp_earnings') || (link.source === 'borrowing_cost' && link.target === 'stock_market');
              const pathString = isCurved
                ? `M${src.x},${src.y} A${dr * 1.2},${dr * 1.2} 0 0,1 ${dest.x},${dest.y}`
                : `M${src.x},${src.y} L${dest.x},${dest.y}`;

              return (
                <g key={idx}>
                  <path
                    d={pathString}
                    fill="none"
                    stroke={lineColor}
                    strokeWidth={strokeWidth}
                    markerEnd={marker}
                    className="transition-all duration-300"
                  />
                  {/* Small circle in the center of edge for hover explanation */}
                  {active && (
                    <circle
                      cx={(src.x + dest.x) / 2}
                      cy={(src.y + dest.y) / 2}
                      r={3}
                      fill="#3b82f6"
                      className="animate-ping"
                    />
                  )}
                </g>
              );
            })}

            {/* Draw Nodes */}
            {nodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const isSource = sourceNodeId === node.id;
              const isTarget = targetNodeId === node.id;
              
              let borderClass = 'stroke-gray-800';
              let fillBg = '#0b0f19';
              let textGlow = 'text-gray-400';

              if (isSource) {
                borderClass = 'stroke-emerald-500 stroke-[2.5px]';
                fillBg = '#022c22';
                textGlow = 'text-emerald-400 font-bold';
              } else if (isTarget) {
                borderClass = 'stroke-blue-500 stroke-[2.5px]';
                fillBg = '#172554';
                textGlow = 'text-blue-300 font-bold';
              } else if (isSelected) {
                borderClass = 'stroke-yellow-500 stroke-[2px]';
                fillBg = '#1e1b4b';
                textGlow = 'text-yellow-400';
              }

              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="cursor-pointer select-none"
                >
                  {/* Outer glowing halo on select */}
                  {isSelected && (
                    <circle r={22} fill="rgba(234, 179, 8, 0.08)" className="pulse-node" />
                  )}
                  {/* Node Circle */}
                  <circle 
                    r={16} 
                    fill={fillBg} 
                    className={`${borderClass} transition-colors duration-300`} 
                  />
                  {/* Category marker */}
                  <circle
                    r={3}
                    cx={12}
                    cy={-12}
                    fill={
                      node.category === 'Commodity' ? '#ef4444' : 
                      node.category === 'Policy Rate' ? '#f59e0b' : 
                      node.category === 'Forex' ? '#10b981' : '#3b82f6'
                    }
                  />
                  {/* Label Text */}
                  <text 
                    y={32} 
                    textAnchor="middle" 
                    fill="currentColor"
                    className={`${textGlow} text-[9px] uppercase font-bold tracking-tight`}
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500 text-xs">
            <Cpu className="w-5 h-5 animate-spin mr-2" /> Loading Macro Knowledge Base...
          </div>
        )}
      </div>

      {/* Control Panel & Details */}
      <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Graph Node Inspector */}
        <div className="border border-gray-800 rounded p-2.5 bg-[#090d16]/30">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1 flex items-center">
            <HelpCircle className="w-3.5 h-3.5 text-yellow-400 mr-1" />
            NODE INSPECTOR
          </h4>
          {selectedNode ? (
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-gray-200 text-xs">{selectedNode.label}</span>
                <span className="text-[9px] px-1 bg-gray-800 text-gray-500 rounded uppercase">
                  {selectedNode.category}
                </span>
              </div>
              <p className="text-gray-400 text-[11px] leading-relaxed">
                {selectedNode.description}
              </p>
              <div className="mt-2 flex gap-1.5">
                <button
                  onClick={() => setSourceNodeId(selectedNode.id)}
                  className="px-2 py-0.5 rounded-sm bg-emerald-600/35 border border-emerald-500/50 text-emerald-400 text-[10px] hover:bg-emerald-600/50"
                >
                  Set as Source
                </button>
                <button
                  onClick={() => setTargetNodeId(selectedNode.id)}
                  className="px-2 py-0.5 rounded-sm bg-blue-600/35 border border-blue-500/50 text-blue-300 text-[10px] hover:bg-blue-600/50"
                >
                  Set as Target
                </button>
              </div>
            </div>
          ) : (
            <span className="text-gray-600 text-[10px]">Click a node on the graph to inspect its details and trace relationships.</span>
          )}
        </div>

        {/* Causality Chain Explainer */}
        <div className="border border-gray-800 rounded p-2.5 bg-[#090d16]/30">
          <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1.5 flex items-center">
            <Cpu className="w-3.5 h-3.5 text-blue-400 mr-1" />
            CAUSALITY ENGINE PATHWAY TRACER
          </h4>
          <div className="flex items-center gap-1 mb-2">
            <span className="text-emerald-400 font-bold text-[10px] uppercase">
              {nodes.find(n => n.id === sourceNodeId)?.label || sourceNodeId}
            </span>
            <ArrowRight className="w-3 h-3 text-gray-600" />
            <span className="text-blue-300 font-bold text-[10px] uppercase">
              {nodes.find(n => n.id === targetNodeId)?.label || targetNodeId}
            </span>
          </div>

          <div className="max-h-24 overflow-y-auto space-y-1.5 pr-1 text-[10px]">
            {loadingCausality ? (
              <span className="text-gray-500">Calculating transmission route...</span>
            ) : causalityChain.length > 0 ? (
              causalityChain.map((step, idx) => (
                <div key={idx} className="border-l border-blue-500/40 pl-2 leading-relaxed text-gray-300">
                  <span className="text-blue-400 font-semibold">{step.source}</span>
                  <span className={`mx-1 font-bold ${step.sign === '+' ? 'text-emerald-400' : 'text-red-400'}`}>
                    [{step.sign}]
                  </span>
                  <span>{step.relationship}</span>
                </div>
              ))
            ) : (
              <span className="text-gray-600">No active causal sequence matches this link combination. Try changing source/target nodes.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

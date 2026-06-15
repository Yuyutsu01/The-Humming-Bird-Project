'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, Terminal, BookOpen, BarChart2, ShieldAlert, Cpu } from 'lucide-react';

interface CommandBarProps {
  isOpen: boolean;
  onClose: () => void;
  onExecuteCommand: (cmd: string) => void;
}

export default function CommandBar({ isOpen, onClose, onExecuteCommand }: CommandBarProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands = [
    { text: 'Switch to Investor Dashboard', cmd: '/dashboard investor', category: 'navigation', icon: BarChart2 },
    { text: 'Switch to Economist Dashboard', cmd: '/dashboard economist', category: 'navigation', icon: Terminal },
    { text: 'Switch to Student Dashboard', cmd: '/dashboard student', category: 'navigation', icon: BookOpen },
    { text: 'Switch to Research Dashboard', cmd: '/dashboard research', category: 'navigation', icon: Search },
    { text: 'Switch to Government Dashboard', cmd: '/dashboard government', category: 'navigation', icon: Cpu },
    { text: 'Simulate Oil Surge ($150)', cmd: '/simulate oil 150', category: 'simulation', icon: ShieldAlert },
    { text: 'Simulate Fed Rate Hike (8%)', cmd: '/simulate fed 8.0', category: 'simulation', icon: ShieldAlert },
    { text: 'Teach inflation (Student Mode)', cmd: '/teach inflation', category: 'education', icon: BookOpen },
    { text: 'Explain Today\'s Move (15yo Mode)', cmd: '/ask Explain today\'s market movement like I\'m 15 years old', category: 'ai', icon: Terminal }
  ];

  const filteredCommands = commands.filter(item =>
    item.text.toLowerCase().includes(query.toLowerCase()) ||
    item.cmd.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % Math.max(1, filteredCommands.length));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % Math.max(1, filteredCommands.length));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          handleSelect(filteredCommands[selectedIndex].cmd);
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands]);

  const handleSelect = (cmd: string) => {
    onExecuteCommand(cmd);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm">
      <div 
        className="w-full max-w-xl border border-gray-800 rounded bg-[#090d16] shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Input area */}
        <div className="flex items-center px-4 border-b border-gray-800">
          <Search className="w-5 h-5 text-gray-500 mr-3" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or ask a question (e.g. /dashboard)..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            className="w-full h-12 bg-transparent text-gray-200 outline-none placeholder-gray-500 font-mono text-sm"
          />
          <kbd className="px-1.5 py-0.5 border border-gray-800 text-[10px] text-gray-500 rounded font-mono">
            ESC
          </kbd>
        </div>

        {/* Results list */}
        <div className="max-h-72 overflow-y-auto p-2">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <button
                  key={item.cmd}
                  onClick={() => handleSelect(item.cmd)}
                  className={`w-full flex items-center px-3 py-2.5 rounded font-mono text-xs text-left transition-colors ${
                    isSelected ? 'bg-blue-600/35 text-blue-300 border border-blue-600/50' : 'text-gray-400 border border-transparent hover:bg-gray-800/40'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-3 text-gray-400" />
                  <div className="flex-1">
                    <span className="font-semibold block">{item.text}</span>
                    <span className="text-[10px] text-gray-500">{item.cmd}</span>
                  </div>
                  <span className="text-[9px] uppercase border border-gray-800 text-gray-500 px-1 py-0.2 rounded">
                    {item.category}
                  </span>
                </button>
              );
            })
          ) : (
            <div className="text-center py-6 text-gray-500 text-xs font-mono">
              No matching commands. Press Enter to search with AI.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useConversation } from '../hooks/useConversation';

interface WorkspaceProps {
  conversationId: string;
  token: string;
}

export default function ActiveInbox({ conversationId, token }: WorkspaceProps) {
  const { messages, lockHolder, isLocked, sendMessage, toast, clearToast } = useConversation(conversationId, token);
  const [input, setInput] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Parse the agent's identity directly out of the JWT payload container safely
  const currentAgentEmail = useMemo(() => {
    if (!token) return 'Agent';
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      // Accessing standard SimpleJWT credential payload claims
      const payload = JSON.parse(jsonPayload);
      return payload.email || payload.username || 'Agent';
    } catch (e) {
      console.error('Failed to resolve JWT security context metadata:', e);
      return 'Agent';
    }
  }, [token]);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Reactive context analyzer
  useEffect(() => {
    if (messages.length > 0) {
      const lastCustomerMessage = [...messages]
        .reverse()
        .find((msg) => msg.sender === 'customer');

      if (lastCustomerMessage) {
        fetchAISuggestion(lastCustomerMessage.message);
      }
    }
  }, [messages, conversationId]);

  const fetchAISuggestion = async (customerText: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/conversations/${conversationId}/suggest-reply/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ message: customerText })
      });
      if (res.ok) {
        const data = await res.json();
        setSuggestion(data.suggestion);
      }
    } catch (err) {
      console.error("AI recommendation dispatch failure:", err);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLocked) return;
    sendMessage(input);
    setInput('');
    setSuggestion('');
  };

  return (
    <div className="flex flex-col h-[650px] max-w-4xl mx-auto border border-slate-200 rounded-xl shadow-xl bg-white overflow-hidden mt-10 font-sans">
      
      {/* Network / Concurrent Exception Errors */}
      {toast && (
        <div className="bg-rose-600 text-white px-4 py-3 text-sm font-medium flex justify-between items-center z-10 shadow-md">
          <div className="flex items-center gap-2">
            <span>⚠️ {toast}</span>
          </div>
          <button onClick={clearToast} className="text-xs bg-rose-700 hover:bg-rose-800 px-2 py-1 rounded font-bold uppercase tracking-wider transition-colors">
            Dismiss
          </button>
        </div>
      )}

      {/* Workspace Header Dashboard */}
      <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/70 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
          <div>
            <h2 className="font-bold text-slate-800 text-lg tracking-tight">Thread Workspace</h2>
            <p className="text-xs text-slate-400 font-medium">Conversation ID: #{conversationId}</p>
          </div>
        </div>
        {lockHolder && (
          <div className={`px-3 py-1.5 rounded-full text-xs font-semibold tracking-wide border shadow-sm transition-colors ${
            isLocked 
              ? 'bg-amber-50 text-amber-800 border-amber-200' 
              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
          }`}>
            {isLocked ? `🔒 Locked by ${lockHolder}` : '✨ Session Reserved by You'}
          </div>
        )}
      </div>

      {/* Message History Grid */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2">
            <span className="text-3xl">📥</span>
            <p className="text-sm font-medium">No messages in this pipeline yet.</p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isAgent = msg.sender === 'agent';
            return (
              <div key={index} className={`flex flex-col ${isAgent ? 'items-end' : 'items-start'} space-y-1`}>
                {/* Dynamically uses the parsed token identifier context instead of the hardcoded fallback tag */}
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1">
                  {isAgent ? `${currentAgentEmail} (Agent)` : 'Customer'}
                </span>
                <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed transition-all ${
                  isAgent 
                    ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-tr-none' 
                    : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none hover:border-slate-300'
                }`}>
                  <p>{msg.message}</p>
                </div>
              </div>
            );
          })
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Context Copilot Recommendation Widget */}
      {suggestion && (
        <div className="mx-4 mb-2 p-3.5 bg-gradient-to-r from-blue-50/80 to-indigo-50/80 border border-blue-100 rounded-xl flex items-start justify-between gap-4 shadow-inner backdrop-blur-md">
          <div className="flex gap-2.5 pt-0.5">
            <span className="text-base shrink-0">💡</span>
            <div className="flex flex-col gap-0.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">Smart Copilot Draft</span>
              <p className="text-xs text-slate-700 italic font-medium leading-relaxed">"{suggestion}"</p>
            </div>
          </div>
          <button 
            onClick={() => { setInput(suggestion); setSuggestion(''); }} 
            type="button" 
            className="text-xs font-bold bg-blue-600 text-white px-3 py-2 rounded-lg shadow-sm hover:bg-blue-700 active:scale-95 transition-all shrink-0 hover:shadow-md"
          >
            Apply Template
          </button>
        </div>
      )}

      {/* Synchronous Output Action Box */}
      <form onSubmit={handleSend} className="p-4 border-t border-slate-100 flex gap-3 bg-white items-center">
        <div className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLocked}
            placeholder={isLocked ? "Composition workspace is currently locked..." : "Type agent response..."}
            className="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-400 placeholder-slate-400"
          />
        </div>
        <button
          type="submit"
          disabled={isLocked || !input.trim()}
          className="px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed shadow-md hover:shadow-lg active:scale-95 disabled:active:scale-100 transition-all duration-200 shrink-0"
        >
          Send Message
        </button>
      </form>
    </div>
  );
}
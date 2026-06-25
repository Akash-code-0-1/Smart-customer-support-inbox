'use client';

import React, { useState } from 'react';
import { useConversation } from '../hooks/useConversation';

interface WorkspaceProps {
  conversationId: string;
  token: string;
}

export default function ActiveInbox({ conversationId, token }: WorkspaceProps) {
  const { messages, lockHolder, isLocked, sendMessage, toast, clearToast } = useConversation(conversationId, token);
  const [input, setInput] = useState('');
  const [suggestion, setSuggestion] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLocked) return;
    sendMessage(input);
    setInput('');
  };

  const fetchAISuggestion = async () => {
    const res = await fetch(`http://localhost:8000/api/conversations/${conversationId}/suggest-reply/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ message: input })
    });
    const data = await res.json();
    setSuggestion(data.suggestion);
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto border border-gray-200 rounded-lg shadow-sm bg-white overflow-hidden mt-10">
      {toast && (
        <div className="bg-red-500 text-white p-3 text-sm flex justify-between items-center transition-all">
          <span>{toast}</span>
          <button onClick={clearToast} className="font-bold underline text-xs">Dismiss</button>
        </div>
      )}

      <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
        <h2 className="font-semibold text-gray-700">Thread Context #{conversationId}</h2>
        {lockHolder && (
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${isLocked ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
            {isLocked ? `Locked by ${lockHolder}` : 'Lock reserved by you'}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'agent' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-lg p-3 text-sm ${msg.sender === 'agent' ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-gray-800 border border-gray-200'}`}>
              <p>{msg.message}</p>
            </div>
          </div>
        ))}
      </div>

      {input && (
        <div className="p-2 bg-blue-50 border-t border-blue-100 flex items-center justify-between px-4">
          <span className="text-xs text-blue-600 italic truncate max-w-[70%]">
            {suggestion ? `Suggestion: "${suggestion}"` : 'AI recommendations available'}
          </span>
          {!suggestion ? (
            <button onClick={fetchAISuggestion} type="button" className="text-xs font-semibold text-blue-700 hover:underline">
              Analyze Context
            </button>
          ) : (
            <button onClick={() => { setInput(suggestion); setSuggestion(''); }} type="button" className="text-xs font-bold text-emerald-700 hover:underline ml-2">
              Apply
            </button>
          )}
        </div>
      )}

      <form onSubmit={handleSend} className="p-4 border-t border-gray-100 flex gap-2 bg-white">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLocked}
          placeholder={isLocked ? "Composition locked by another agent..." : "Type agent response..."}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={isLocked || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}
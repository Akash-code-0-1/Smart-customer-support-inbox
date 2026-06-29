"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { useConversation } from "../hooks/useConversation";

interface WorkspaceProps {
  conversationId: string;
  token: string;
}

export default function ActiveInbox({ conversationId, token }: WorkspaceProps) {
  const {
    messages,
    lockHolder,
    isLocked,
    sendMessage,
    toast,
    clearToast,
    data,
  } = useConversation(conversationId, token);
  const [input, setInput] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const premadeMacros = [
    {
      label: "👋 Greeting",
      text: "Hello! Thank you for reaching out to customer support today. How can I assist you?",
    },
    {
      label: "💰 Refund",
      text: "We apologize for the inconvenience. I have initiated a full refund back to your original payment method.",
    },
    {
      label: "📦 Shipping",
      text: "Let me track that delivery status for you. Could you please provide your order confirmation number?",
    },
    {
      label: "🔧 Replace",
      text: "I am sorry that your item arrived damaged. I have dispatched a free replacement unit to your address.",
    },
    {
      label: "❌ Cancel",
      text: "I can help you process your account cancellation right away. Please confirm if you would like me to proceed.",
    },
  ];

  // Decode username context straight out of JWT
  const agentIdentifier = useMemo(() => {
    if (!token) return "Agent";
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join(""),
      );
      const payload = JSON.parse(jsonPayload);
      return payload.username || payload.email || "Agent";
    } catch (e) {
      return "Agent";
    }
  }, [token]);

  // Dynamically pull Customer Name field metadata out of the API response payload
  const customerName = useMemo(() => {
    return data?.customer_name || data?.customer || "Customer";
  }, [data]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLocked) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[650px] max-w-4xl mx-auto border border-slate-200 rounded-xl shadow-xl bg-white overflow-hidden mt-10 font-sans relative">
      {toast && (
        <div className="bg-rose-600 text-white px-4 py-3 text-sm font-medium flex justify-between items-center z-10 shadow-md">
          <span>{toast}</span>
          <button
            onClick={clearToast}
            className="text-xs bg-rose-700 px-2 py-1 rounded font-bold uppercase tracking-wider"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header Dashboard View */}
      <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/70 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400" />
          <div>
            <h2 className="font-bold text-slate-800 text-base tracking-tight">
              Chatting with {customerName}
            </h2>
            
            <div className="flex items-center gap-2 mt-0.5">
              <p className="text-xs text-slate-400 font-medium">
                Support Case Matrix • ID #{conversationId}
              </p>
              
              {data?.sentiment && (
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                    data.sentiment.toLowerCase() === "positive"
                      ? "bg-emerald-100 text-emerald-800"
                      : data.sentiment.toLowerCase() === "negative"
                        ? "bg-rose-100 text-rose-800"
                        : "bg-slate-100 text-slate-700"
                  }`}
                >
                  {data.sentiment}
                </span>
              )}


            </div>
          </div>
        </div>
        {lockHolder && (
          <div
            className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
              isLocked
                ? "bg-amber-50 text-amber-800 border-amber-200 shadow-inner"
                : "bg-slate-100 text-slate-700 border-slate-200"
            }`}
          >
            {isLocked ? `🔒 Handled by ${lockHolder}` : "✨ Assigned to You"}
          </div>
        )}
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">
        {messages.map((msg, index) => {
          // Dynamic Verification Line: If sender isn't explicitly 'customer', it's an outbound agent action
          const isAgent = msg.sender?.toLowerCase() !== "customer";
          const messageContent = msg.message || msg.text || "";

          // Format structural timestamp field values cleanly
          const messageTime = msg.created_at
            ? new Date(msg.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })
            : new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              });

          return (
            <div
              key={index}
              className={`flex flex-col ${isAgent ? "items-end" : "items-start"} space-y-1`}
            >
              {/* Meta Label Row with Sender Context and Dynamic Timestamps */}
              <div className="flex items-center gap-1.5 px-1 text-[10px] font-bold text-slate-400 tracking-wider uppercase">
                <span>{isAgent ? agentIdentifier : customerName}</span>
                <span className="text-[9px] font-normal text-slate-400/70">
                  • {messageTime}
                </span>
              </div>

              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed transition-all ${
                  isAgent
                    ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-tr-none"
                    : "bg-white text-slate-800 border border-slate-200 rounded-tl-none"
                }`}
              >
                <p>{messageContent}</p>
              </div>
            </div>
          );
        })}
        <div ref={chatEndRef} />
      </div>

      {/* Circular Floating Speed-Dial Navigation Menu */}
      <div className="absolute bottom-20 right-6 flex flex-col items-end gap-2 z-30">
        {menuOpen && (
          <div className="flex flex-col gap-2 bg-white/90 backdrop-blur-md p-2 rounded-xl border border-slate-200 shadow-xl transition-all max-w-xs animate-fade-in">
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase px-2 pb-1 block border-b border-slate-100">
              AI Quick Macros
            </span>
            {premadeMacros.map((macro, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setInput(macro.text);
                  setMenuOpen(false);
                }}
                className="text-left text-xs font-semibold px-3 py-2 text-slate-700 hover:bg-blue-50 rounded-lg hover:text-blue-700 transition-colors truncate w-full"
                title={macro.text}
              >
                {macro.label}
              </button>
            ))}
          </div>
        )}

        <button
          type="button"
          onClick={() => setMenuOpen(!menuOpen)}
          className={`w-12 h-12 rounded-full text-lg shadow-lg flex items-center justify-center transition-all active:scale-95 text-white ${
            menuOpen
              ? "bg-slate-700 ring-4 ring-slate-200"
              : "bg-blue-600 hover:bg-blue-700 ring-4 ring-blue-100"
          }`}
        >
          {menuOpen ? "✖" : "🤖"}
        </button>
      </div>

      {/* Input Action Panel */}
      <form
        onSubmit={handleSend}
        className="p-4 border-t border-slate-100 flex gap-3 bg-white items-center"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLocked}
          placeholder={
            isLocked
              ? "Workspace is locked..."
              : "Type agent response or open AI Assist..."
          }
          className="flex-1 px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:bg-slate-50"
        />
        <button
          type="submit"
          disabled={isLocked || !input.trim()}
          className="px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400 transition-all duration-200"
        >
          Send
        </button>
      </form>
    </div>
  );
}
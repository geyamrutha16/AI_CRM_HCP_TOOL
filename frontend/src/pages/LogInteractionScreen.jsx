import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import ChatInterface from "../components/ChatInterface";
import InteractionForm from "../components/InteractionForm";
import InteractionList from "../components/InteractionList";
import { systemAPI } from "../services/api";
import { toast } from "react-toastify";
import "./LogInteractionScreen.css";

/**
 * LogInteractionScreen - Main page
 * Combines Chat Interface, Form, and Interaction List
 * Allows toggling between different views
 */
export function LogInteractionScreen() {
  const dispatch = useDispatch();
  const [view, setView] = useState("split"); // 'chat', 'form', 'list', 'split'
  const [systemHealthy, setSystemHealthy] = useState(false);

  // Check system health on mount
  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await systemAPI.health();
      setSystemHealthy(response.status === "healthy");
    } catch {
      setSystemHealthy(false);
    }
  };

  return (
    <div className="log-interaction-screen">
      {/* Header */}
      <div className="screen-header">
        <div className="header-left">
          <h1>🏥 AI-CRM Healthcare Interaction Logger</h1>
          <p>Log and manage HCP interactions with AI assistance</p>
        </div>
        <div className="header-right">
          <div
            className={`health-indicator ${systemHealthy ? "healthy" : "unhealthy"}`}
          >
            <span className="health-dot"></span>
            {systemHealthy ? "System Online" : "System Offline"}
          </div>
        </div>
      </div>

      {/* Tabs/Navigation */}
      <div className="view-tabs">
        <button
          className={`tab ${view === "split" ? "active" : ""}`}
          onClick={() => setView("split")}
        >
          👥 Split View
        </button>
        <button
          className={`tab ${view === "chat" ? "active" : ""}`}
          onClick={() => setView("chat")}
        >
          💬 Chat Mode
        </button>
        <button
          className={`tab ${view === "form" ? "active" : ""}`}
          onClick={() => setView("form")}
        >
          📋 Form Mode
        </button>
        <button
          className={`tab ${view === "list" ? "active" : ""}`}
          onClick={() => setView("list")}
        >
          📊 All Interactions
        </button>
      </div>

      {/* Content Area */}
      <div className="screen-content">
        {/* Split View (Default) */}
        {view === "split" && (
          <div className="split-layout">
            <div className="form-panel">
              <InteractionForm />
            </div>
            <div className="divider"></div>
            <div className="chat-panel">
              <ChatInterface />
            </div>
          </div>
        )}

        {/* Chat Only */}
        {view === "chat" && (
          <div className="single-panel">
            <ChatInterface />
          </div>
        )}

        {/* Form Only */}
        {view === "form" && (
          <div className="single-panel">
            <InteractionForm />
          </div>
        )}

        {/* List Only */}
        {view === "list" && (
          <div className="single-panel">
            <InteractionList />
          </div>
        )}
      </div>

      {/* Info Panel */}
      <div className="info-panel">
        <div className="info-item">
          <span className="info-label">💡 Tip:</span>
          <span className="info-text">
            Use the chat to have a natural conversation, or fill in the form for
            structured input
          </span>
        </div>
      </div>
    </div>
  );
}

export default LogInteractionScreen;

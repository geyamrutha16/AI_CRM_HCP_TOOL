import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addMessage, setLoading, setError } from "../store/chatSlice";
import { agentAPI } from "../services/api";
import { toast } from "react-toastify";
import "./ChatInterface.css";

/**
 * ChatInterface Component
 * Provides a ChatGPT-like interface for conversational interaction logging.
 * - User can type messages
 * - AI agent processes and responds
 * - Displays chat history
 * - Shows loading states and error handling
 */
export function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message to chat
    dispatch(
      addMessage({
        role: "user",
        content: inputValue,
      }),
    );

    const messageText = inputValue;
    setInputValue("");
    dispatch(setLoading(true));

    try {
      // Call agent API
      const response = await agentAPI.runAgent(messageText);

      // Add AI response to chat
      dispatch(
        addMessage({
          role: "assistant",
          content: response.ai_message,
          toolUsed: response.tool_used,
          structuredData: response.structured_data,
          interactionId: response.interaction_id,
        }),
      );

      // Show success toast if interaction was created
      if (response.interaction_id) {
        toast.success(`Interaction #${response.interaction_id} created!`, {
          position: "bottom-right",
          autoClose: 3000,
        });
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to process message";
      dispatch(setError(errorMessage));
      toast.error(errorMessage, {
        position: "bottom-right",
        autoClose: 3000,
      });
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleVoiceInput = async () => {
    // Placeholder for voice input functionality
    toast.info("Voice input coming soon!", { autoClose: 3000 });
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>🤖 AI Assistant</h2>
        <p>Chat to log interactions with HCPs</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="empty-icon">💬</div>
            <p>Start a conversation to log an interaction</p>
            <small>Try: "I met with Dr. Smith to discuss Product X"</small>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message chat-message-${message.role}`}
          >
            <div className="message-avatar">
              {message.role === "user" ? "👤" : "🤖"}
            </div>
            <div className="message-content">
              <p className="message-text">{message.content}</p>
              {message.toolUsed && (
                <small className="message-tool">Tool: {message.toolUsed}</small>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message chat-message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSendMessage} className="chat-form">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Describe your HCP interaction..."
              disabled={loading}
              className="chat-input"
            />
            <button
              type="button"
              onClick={handleVoiceInput}
              className="voice-button"
              disabled={loading}
              title="Voice input"
            >
              🎤
            </button>
          </div>
          <button
            type="submit"
            disabled={loading || !inputValue.trim()}
            className="send-button"
          >
            {loading ? "⏳" : "➤"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatInterface;

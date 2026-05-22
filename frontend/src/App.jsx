import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "/api";

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function UserAvatar() {
  return (
    <svg className="message-avatar" viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle cx="16" cy="16" r="16" fill="url(#userGrad)" />
      <path d="M16 14c3.3 0 6 2.2 6 5v2H10v-2c0-2.8 2.7-5 6-5z" fill="#fff" opacity="0.9" />
      <circle cx="16" cy="10" r="3.5" fill="#fff" opacity="0.9" />
      <defs>
        <linearGradient id="userGrad" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#4f46e5" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function AssistantAvatar() {
  return (
    <svg className="message-avatar" viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle cx="16" cy="16" r="16" fill="url(#asstGrad)" />
      <rect x="9" y="10" width="14" height="12" rx="3" fill="#fff" opacity="0.9" />
      <circle cx="13" cy="16" r="1.5" fill="#6366f1" />
      <circle cx="19" cy="16" r="1.5" fill="#6366f1" />
      <rect x="11" y="19" width="10" height="1.5" rx="0.75" fill="#6366f1" opacity="0.5" />
      <defs>
        <linearGradient id="asstGrad" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#0891b2" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [text]);

  return (
    <button
      className="copy-button"
      onClick={handleCopy}
      aria-label={copied ? "Copied to clipboard" : "Copy message to clipboard"}
      title={copied ? "Copied!" : "Copy"}
    >
      {copied ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      )}
      <span>{copied ? "Copied" : "Copy"}</span>
    </button>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const askChatbot = async (queryText) => {
    const textToSend = typeof queryText === "string" ? queryText : question;
    if (!textToSend.trim()) return;

    const userMessage = { role: "user", content: textToSend, timestamp: formatTime(new Date()) };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        question: textToSend,
        conversation_id: conversationId,
      });

      const data = response.data;

      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage = {
        role: "assistant",
        content: data.answer || "No response from agent.",
        structured_data: data.structured_data || [],
        steps: data.steps || [],
        timestamp: formatTime(new Date()),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = err.response?.data?.detail || err.message || "Failed to connect to server";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorMsg}`, is_error: true, timestamp: formatTime(new Date()) },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askChatbot();
    }
  };

  const startNewConversation = () => {
    setConversationId(null);
    setMessages([]);
  };

  const renderStructuredData = (data) => {
    if (!data || data.length === 0) return null;

    return data.map((section, index) => {
      if (!section || !section.type) return null;

      return (
        <div key={index} className="structured-section">
          {section.title && (
            <h3 className="section-header">
              {section.title}
              {section.count !== undefined && (
                <span className="result-count">
                  {section.count} result{section.count !== 1 ? "s" : ""}
                </span>
              )}
            </h3>
          )}

          {section.type === "table" && Array.isArray(section.data) && section.data.length > 0 && (
            <div className="table-scroll">
              <table className="table-data">
                <thead>
                  <tr>
                    {Object.keys(section.data[0]).map((key) => (
                      <th key={key}>
                        {key.replace(/_/g, " ")}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {section.data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {Object.values(row).map((value, colIndex) => (
                        <td key={colIndex}>
                          {value === null || value === undefined ? "-" : String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {section.type === "table" && (!section.data || section.data.length === 0) && (
            <p style={{ color: "var(--text-muted)", fontStyle: "italic", margin: 0 }}>
              No matching records found.
            </p>
          )}

          {section.type === "analytics" && section.data && typeof section.data === "object" && (
            <div className="analytics-flex">
              {Object.entries(section.data).map(([key, value]) => (
                <div key={key} className="metric-widget">
                  <div className="metric-label">
                    {key.replace(/_/g, " ")}
                  </div>
                  <div className="metric-value">
                    {typeof value === "number" ? Number(value.toFixed(2)) : String(value)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {section.type === "message" && section.data?.message && (
            <div className="status-message">
              {section.data.message}
            </div>
          )}

          {section.type === "error" && section.data?.message && (
            <div className="error-message">
              {section.data.message}
            </div>
          )}
        </div>
      );
    });
  };

  const renderSteps = (steps) => {
    if (!steps || steps.length === 0) return null;
    return (
      <details className="agent-steps-accordion">
        <summary className="agent-steps-summary">
          Agent Steps ({steps.length} tool call{steps.length > 1 ? "s" : ""})
        </summary>
        <div className="agent-steps-content">
          {steps.map((step, i) => (
            <div key={i} className="agent-step-item">
              <span className="agent-step-tool-name">{step.tool}</span>
              {step.tool_input && Object.keys(step.tool_input).length > 0 && (
                <span className="agent-step-inputs"> ({JSON.stringify(step.tool_input)})</span>
              )}
            </div>
          ))}
        </div>
      </details>
    );
  };

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="app-header">
        <div className="header-info">
          <h1>AI Student Database Chatbot</h1>
          <p>Explore students, teachers, and courses with AI multi-step reasoning</p>
        </div>
        <div className="header-controls">
          <div className="db-status-badge">
            <span className="status-dot"></span>
            Database Connected
          </div>
          {conversationId && (
            <button
              className="new-chat-button"
              onClick={startNewConversation}
              aria-label="Start a new conversation"
            >
              New Chat
            </button>
          )}
        </div>
      </header>

      {/* MESSAGES WINDOW */}
      <div className="chat-window">
        <div className="messages-list">
          {messages.length === 0 && (
            <div className="welcome-screen">
              <div className="welcome-logo">&#x1F393;</div>
              <h2>Welcome to AI Database Chatbot</h2>
              <p>
                Ask questions about students, courses, grades, or teachers. The AI agent will plan and execute multi-step database operations to answer your query.
              </p>

              <div className="suggestions-grid">
                <button className="suggestion-card" onClick={() => askChatbot("Show all students")} aria-label="Ask: Show all students">
                  Show all students
                </button>
                <button className="suggestion-card" onClick={() => askChatbot("Who is the topper?")} aria-label="Ask: Who is the topper?">
                  Who is the topper?
                </button>
                <button className="suggestion-card" onClick={() => askChatbot("How many students are enrolled per course?")} aria-label="Ask: Students enrolled per course">
                  Students enrolled per course
                </button>
                <button className="suggestion-card" onClick={() => askChatbot("Add a student named Sam with 92 marks in course 1")} aria-label="Ask: Add a student named Sam">
                  Add Sam with 92 marks to course 1
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-wrapper ${msg.role} ${msg.is_error ? "error-msg" : ""} message-fade-in`}
            >
              {msg.role === "user" ? <UserAvatar /> : <AssistantAvatar />}
              <div className="message-content-col">
                <div className="message-bubble">
                  <div style={{ fontSize: "14.5px", whiteSpace: "pre-wrap" }}>{msg.content}</div>
                  {msg.structured_data && msg.structured_data.length > 0 && (
                    <div>
                      {renderStructuredData(msg.structured_data)}
                    </div>
                  )}
                  {msg.steps && msg.steps.length > 0 && renderSteps(msg.steps)}
                </div>
                <div className="message-meta">
                  {msg.timestamp && <span className="message-timestamp">{msg.timestamp}</span>}
                  {msg.role === "assistant" && !msg.is_error && (
                    <CopyButton text={msg.content} />
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-wrapper assistant message-fade-in">
              <AssistantAvatar />
              <div className="typing-bubble">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* INPUT PANEL */}
        <div className="chat-input-container">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the database..."
            disabled={loading}
            aria-label="Type your question about the database"
          />
          <button
            onClick={() => askChatbot()}
            disabled={loading || !question.trim()}
            className="send-button-main"
            aria-label={loading ? "Waiting for response" : "Send question"}
          >
            {loading ? (
              <span className="spinner-icon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
              </span>
            ) : (
              "Ask"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

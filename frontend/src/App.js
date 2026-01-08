import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Get API URL - use relative path for Vercel, localhost for development
  const API_URL = process.env.NODE_ENV === 'production' 
    ? '/api/chat' 
    : 'http://localhost:5000/api/chat';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const clearChat = () => {
    setMessages([]);
    setError(null);
    inputRef.current?.focus();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage.content }),
      });

      const data = await response.json();

      if (data.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer,
          source: data.source_page
        }]);
      } else {
        setError(data.error || 'An error occurred');
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${data.error || 'Unknown error'}. Please try again.`,
          error: true
        }]);
      }
    } catch (error) {
      setError('Failed to connect to the server');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to connect to the server. Please check your connection and try again.',
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <div className="header-content">
          <h1>🏥 Medical Encyclopedia Chatbot</h1>
          {messages.length > 0 && (
            <button onClick={clearChat} className="clear-button" title="Clear chat">
              🗑️ Clear
            </button>
          )}
        </div>
      </div>
      
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">💬</div>
            <h2>Welcome to Medical Encyclopedia Chatbot</h2>
            <p>Ask me anything about medical topics from the encyclopedia!</p>
            <div className="example-questions">
              <p className="examples-title">Try asking:</p>
              <div className="example-chips">
                <button 
                  className="example-chip"
                  onClick={() => setInput("What is chemotherapy?")}
                >
                  What is chemotherapy?
                </button>
                <button 
                  className="example-chip"
                  onClick={() => setInput("How does diabetes work?")}
                >
                  How does diabetes work?
                </button>
                <button 
                  className="example-chip"
                  onClick={() => setInput("What are the symptoms of flu?")}
                >
                  What are the symptoms of flu?
                </button>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-banner">
            ⚠️ {error}
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              <div className="message-header">
                <span>{message.role === 'user' ? '👤 You' : '🤖 Assistant'}</span>
                {message.role === 'assistant' && (
                  <button 
                    onClick={() => copyToClipboard(message.content)}
                    className="copy-button"
                    title="Copy message"
                  >
                    📋
                  </button>
                )}
              </div>
              <div className={`message-text ${message.error ? 'error-text' : ''}`}>
                {message.content.split('\n').map((line, i) => (
                  <React.Fragment key={i}>
                    {line}
                    {i < message.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
              {message.source && !message.error && (
                <div className="message-source">
                  📄 Source: Page {message.source}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="message-header">🤖 Assistant</div>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="input-container" onSubmit={sendMessage}>
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about medical topics... (Press Enter to send, Shift+Enter for new line)"
            disabled={loading}
            className="input-field"
            rows="1"
            style={{ resize: 'none', minHeight: '24px', maxHeight: '200px' }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="send-button"
            title="Send message (Enter)"
          >
            {loading ? (
              <div className="spinner"></div>
            ) : (
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </button>
        </div>
        <div className="input-footer">
          <span className="footer-text">Press Enter to send • Shift+Enter for new line</span>
        </div>
      </form>
    </div>
  );
}

export default App;


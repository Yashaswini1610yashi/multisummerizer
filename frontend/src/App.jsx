import React, { useState, useRef, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am your Multilingual PDF Assistant. Please upload a PDF to get started.' }
  ]);
  const [input, setInput] = useState('');
  const [summary, setSummary] = useState('');
  const [summaryStyle, setSummaryStyle] = useState('Detailed Summary');
  const [targetLang, setTargetLang] = useState('en');
  const [detectedLang, setDetectedLang] = useState('');
  
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setSessionId(data.session_id);
      setDetectedLang(data.detected_lang);
      
      setMessages(prev => [...prev, 
        { role: 'bot', text: `Successfully uploaded "${uploadedFile.name}". Detected language: ${data.detected_lang}. Generating summary...` }
      ]);

      // Trigger initial summary
      handleSummarize(data.session_id);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'bot', text: 'Error: Failed to process document.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (sid = sessionId, style = summaryStyle, lang = targetLang) => {
    if (!sid) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid, style, language: lang }),
      });

      if (!response.ok) throw new Error('Summary failed');

      const data = await response.json();
      setSummary(data.summary);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !sessionId || loading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: sessionId, 
          message: userMessage, 
          language: targetLang 
        }),
      });

      if (!response.ok) throw new Error('Chat failed');

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.response }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'bot', text: 'I could not find this information in the uploaded document.' }]);
    } finally {
      setLoading(false);
    }
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'hi', name: 'Hindi' },
    { code: 'ar', name: 'Arabic' }
  ];

  const styles = ['Short Summary', 'Detailed Summary', 'Bullet Points', 'Explain Like I’m 5'];

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2>Document Hub</h2>
        <div className="glass-card">
          <p style={{ marginBottom: '1rem', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
            Upload a PDF to analyze and summarize.
          </p>
          <input 
            type="file" 
            accept=".pdf" 
            id="pdf-upload" 
            hidden 
            onChange={handleFileUpload} 
          />
          <label htmlFor="pdf-upload" className="btn" style={{ display: 'block', width: '100%', boxSizing: 'border-box' }}>
            {sessionId ? 'Update Document' : 'Upload PDF'}
          </label>
        </div>

        {sessionId && (
          <div className="glass-card">
            <h3>Summary Options</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)' }}>Output Language</label>
                <select 
                  value={targetLang} 
                  onChange={(e) => {
                    setTargetLang(e.target.value);
                    handleSummarize(sessionId, summaryStyle, e.target.value);
                  }}
                  style={{ width: '100%' }}
                >
                  {languages.map(l => <option key={l.code} value={l.code}>{l.name}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)' }}>Summary Style</label>
                <select 
                  value={summaryStyle} 
                  onChange={(e) => {
                    setSummaryStyle(e.target.value);
                    handleSummarize(sessionId, e.target.value, targetLang);
                  }}
                  style={{ width: '100%' }}
                >
                  {styles.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
          </div>
        )}

        {summary && (
          <div className="glass-card" style={{ flex: 1, overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>Summary</h3>
              {loading && <div className="loader" style={{ fontSize: '0.7rem' }}>Updating...</div>}
            </div>
            <div className="summary-content">
              {summary}
            </div>
          </div>
        )}
      </div>

      <div className="main-chat">
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.text}
            </div>
          ))}
          {loading && <div className="message bot">Thinking...</div>}
          <div ref={chatEndRef} />
        </div>
        
        <form className="chat-input-area" onSubmit={handleSendMessage}>
          <input 
            className="input-field" 
            placeholder={sessionId ? "Ask anything about the document..." : "Please upload a PDF first."} 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!sessionId || loading}
          />
          <button className="btn" disabled={!sessionId || loading}>Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;

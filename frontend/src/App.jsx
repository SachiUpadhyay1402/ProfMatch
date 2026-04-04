import { useState, useRef, useEffect } from "react";

const SUGGESTIONS = [
  "Who works on machine learning at MIT?",
  "Find faculty in the robotics department",
  "Show me professors working on climate change",
  "Who are the top AI researchers at MIT?",
  "Find faculty with expertise in neuroscience",
  "Who is the head of CSAIL?",
];

const THEMES = {
  light: {
    bg: "#ffffff",
    navBg: "#ffffff",
    navBorder: "#e8e8e8",
    text: "#111111",
    subText: "#666666",
    inputBg: "#ffffff",
    inputBorder: "#d0d0d0",
    cardBg: "#ffffff",
    cardBorder: "#e8e8e8",
    cardHover: "#f5f5f5",
    bubbleBot: "#f5f5f5",
    bubbleBotBorder: "#e8e8e8",
    bubbleBotText: "#111111",
    bubbleUser: "#111111",
    bubbleUserText: "#ffffff",
    botAvatar: "#eeeeee",
    iconWrap: "#eeeeee",
    sendBtn: "#111111",
    sendBtnText: "#ffffff",
    disclaimer: "#aaaaaa",
    navIcon: "#555555",
  },
  dark: {
    bg: "#0d0d0d",
    navBg: "#0d0d0d",
    navBorder: "#222222",
    text: "#f0f0f0",
    subText: "#888888",
    inputBg: "#1a1a1a",
    inputBorder: "#333333",
    cardBg: "#1a1a1a",
    cardBorder: "#2a2a2a",
    cardHover: "#222222",
    bubbleBot: "#1a1a1a",
    bubbleBotBorder: "#2a2a2a",
    bubbleBotText: "#f0f0f0",
    bubbleUser: "#f0f0f0",
    bubbleUserText: "#111111",
    botAvatar: "#222222",
    iconWrap: "#222222",
    sendBtn: "#f0f0f0",
    sendBtnText: "#111111",
    disclaimer: "#555555",
    navIcon: "#888888",
  },
};

const BACKEND_URL = "http://localhost:8000";

function SuggestionCard({ text, t, onClick }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex", alignItems: "center", gap: 12,
        background: hovered ? t.cardHover : t.cardBg,
        border: `1px solid ${t.cardBorder}`,
        borderRadius: 10, padding: "14px 16px", cursor: "pointer",
        textAlign: "left", fontFamily: "inherit", fontSize: 14,
        color: t.text, transition: "background 0.15s", width: "100%",
      }}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={t.subText} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <span style={{ lineHeight: 1.4 }}>{text}</span>
    </button>
  );
}

function FacultyCard({ f, t }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div style={{
      background: t.cardBg,
      border: `1px solid ${t.cardBorder}`,
      borderRadius: 14,
      padding: "20px",
      margin: "12px 0",
      boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
      transition: "transform 0.2s, box-shadow 0.2s",
      width: "100%",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div>
          <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 4px 0", color: t.text }}>{f.name}</h3>
          <p style={{ fontSize: 14, color: t.subText, margin: 0 }}>{f.designation}</p>
        </div>
        <div style={{ textAlign: "right", background: "#f0f7ff", padding: "4px 10px", borderRadius: 8, border: "1px solid #cce3ff" }}>
          <span style={{ fontSize: 10, color: "#0056b3", fontWeight: 700, display: "block", textTransform: "uppercase" }}>Match Score</span>
          <span style={{ fontSize: 16, color: "#0056b3", fontWeight: 800 }}>{(f.score * 100).toFixed(1)}%</span>
        </div>
      </div>

      {f.website_expertise && f.website_expertise !== "nan" && (
        <div style={{ marginBottom: 10, background: "rgba(0, 122, 255, 0.05)", borderLeft: "4px solid #007aff", padding: "8px 12px", borderRadius: "0 6px 6px 0" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: "#007aff", marginBottom: 4 }}>Website Expertise</p>
          <p style={{ fontSize: 13, lineHeight: 1.5, color: t.text }}>{f.website_expertise}</p>
        </div>
      )}

      {f.scholar_expertise && f.scholar_expertise !== "nan" && (
        <div style={{ marginBottom: 10, background: "rgba(52, 199, 89, 0.05)", borderLeft: "4px solid #34c759", padding: "8px 12px", borderRadius: "0 6px 6px 0" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: "#34c759", marginBottom: 4 }}>Scholar Expertise</p>
          <p style={{ fontSize: 13, lineHeight: 1.5, color: t.text }}>{f.scholar_expertise}</p>
        </div>
      )}

      {f.bio && f.bio.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <button 
            onClick={() => setExpanded(!expanded)}
            style={{ background: "none", border: "none", color: "#007aff", fontSize: 13, fontWeight: 600, cursor: "pointer", padding: 0, display: "flex", alignItems: "center", gap: 4 }}
          >
            {expanded ? "Hide Bio ↑" : "Show About ↓"}
          </button>
          {expanded && (
            <p style={{ fontSize: 13, lineHeight: 1.6, color: t.subText, marginTop: 10, borderTop: `1px solid ${t.cardBorder}`, paddingTop: 10 }}>
              {f.bio}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function MITFacultyAI() {
  const [theme, setTheme] = useState("light");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const messagesEndRef = useRef(null);
  const t = THEMES[theme];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const toggleTheme = () => setTheme((p) => (p === "light" ? "dark" : "light"));

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput("");
    setStarted(true);
    
    const newMessages = [...messages, { role: "user", text: msg }];
    setMessages(newMessages);
    setLoading(true);

    try {
      // Call local FastAPI backend
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newMessages.map((m) => ({ 
            role: m.role === "bot" ? "assistant" : "user", 
            content: m.text 
          })),
          query: msg
        }),
      });

      if (!res.ok) throw new Error("Backend error");
      
      const data = await res.json();
      const reply = data.reply || "Sorry, I couldn't get a response.";
      const faculty = data.faculty || [];
      
      setMessages((prev) => [...prev, { role: "bot", text: reply, faculty }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: "bot", text: "Something went wrong connecting to the backend. Please ensure the FastAPI server is running on port 8000." }]);
    }
    setLoading(false);
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: t.bg, fontFamily: "'Inter', sans-serif", color: t.text, transition: "background 0.3s, color 0.3s" }}>

      {/* NAV */}
      <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 2rem", height: 58, background: t.navBg, borderBottom: `1px solid ${t.navBorder}`, position: "sticky", top: 0, zIndex: 10, transition: "background 0.3s, border-color 0.3s" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 34, height: 34, background: t.text, borderRadius: 6, display: "grid", placeItems: "center", transition: "background 0.3s" }}>
            <span style={{ color: t.bg, fontSize: 11, fontWeight: 800, letterSpacing: 0.5, transition: "color 0.3s" }}>MIT</span>
          </div>
          <span style={{ fontSize: 14, fontWeight: 500 }}><b>MIT</b> Faculty Search</span>
        </div>

        <div style={{ display: "flex", gap: "1.8rem" }}>
          {["Departments", "Research Areas", "Labs & Centers", "About"].map((l) => (
            <span key={l} style={{ fontSize: 14, color: t.navIcon, cursor: "pointer", transition: "color 0.3s" }}>{l} ›</span>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            style={{
              width: 52, height: 28, borderRadius: 14,
              border: `1.5px solid ${t.navBorder}`,
              background: theme === "dark" ? "#f0f0f0" : "#111111",
              cursor: "pointer", position: "relative",
              transition: "background 0.3s, border-color 0.3s", padding: 0,
            }}
          >
            {/* sliding circle with SVG icon */}
            <span style={{
              position: "absolute", top: 3,
              left: theme === "dark" ? 26 : 3,
              width: 20, height: 20, borderRadius: "50%",
              background: theme === "dark" ? "#111111" : "#ffffff",
              transition: "left 0.25s, background 0.3s",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              {theme === "dark" ? (
                /* Moon icon */
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#f0f0f0" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              ) : (
                /* Sun icon */
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#111111" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5" />
                  <line x1="12" y1="1" x2="12" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="23" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                  <line x1="1" y1="12" x2="3" y2="12" />
                  <line x1="21" y1="12" x2="23" y2="12" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              )}
            </span>
          </button>

          {/* Bell icon */}
          <button onClick={() => {}} style={{ background: "none", border: "none", cursor: "pointer", padding: 4, display: "grid", placeItems: "center" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={t.navIcon} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </button>

          <div style={{ width: 32, height: 32, borderRadius: "50%", background: t.text, color: t.bg, fontSize: 12, fontWeight: 700, display: "grid", placeItems: "center", cursor: "pointer", transition: "background 0.3s, color 0.3s" }}>MM</div>
        </div>
      </nav>

      {/* MAIN */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflowY: "auto", paddingBottom: 110 }}>
        {!started ? (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "3rem 1rem" }}>
            <div style={{ width: 68, height: 68, borderRadius: "50%", background: t.iconWrap, display: "grid", placeItems: "center", marginBottom: "1.4rem", transition: "background 0.3s" }}>
              <span style={{ fontSize: 26, color: t.text }}>✦</span>
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, textAlign: "center" }}>MIT Faculty AI</h1>
            <p style={{ fontSize: 14, color: t.subText, marginBottom: "2.2rem", textAlign: "center", transition: "color 0.3s" }}>
              Your smart assistant for finding MIT faculty and research
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, width: "100%", maxWidth: 680 }}>
              {SUGGESTIONS.map((sg, i) => (
                <SuggestionCard key={i} text={sg} t={t} onClick={() => sendMessage(sg)} />
              ))}
            </div>
          </div>
        ) : (
          <div style={{ flex: 1, maxWidth: 760, width: "100%", margin: "0 auto", padding: "2rem 1rem", display: "flex", flexDirection: "column", gap: 20 }}>
            {messages.map((m, i) => (
              <div key={i}>
                <div style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", alignItems: "flex-start", gap: 12, marginBottom: 8 }}>
                  {m.role === "bot" && (
                    <div style={{ width: 32, height: 32, borderRadius: "50%", background: t.iconWrap, display: "grid", placeItems: "center", fontSize: 13, flexShrink: 0, marginTop: 2, color: t.text, transition: "background 0.3s" }}>✦</div>
                  )}
                  <div style={m.role === "user"
                    ? { background: t.bubbleUser, color: t.bubbleUserText, borderRadius: "14px 14px 4px 14px", padding: "12px 16px", fontSize: 14, lineHeight: 1.65, maxWidth: "78%", transition: "background 0.3s" }
                    : { background: t.bubbleBot, border: `1px solid ${t.bubbleBotBorder}`, color: t.bubbleBotText, borderRadius: "4px 14px 14px 14px", padding: "12px 16px", fontSize: 14, lineHeight: 1.65, maxWidth: "78%", transition: "background 0.3s" }
                  }>
                    {m.text.split("\n").map((line, j, arr) => (
                      <span key={j}>{line}{j < arr.length - 1 && <br />}</span>
                    ))}
                  </div>
                </div>
                
                {m.role === "bot" && m.faculty && m.faculty.length > 0 && (
                  <div style={{ paddingLeft: 44, width: "100%" }}>
                    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                      {m.faculty.map((f, idx) => (
                        <FacultyCard key={idx} f={f} t={t} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", background: t.iconWrap, display: "grid", placeItems: "center", fontSize: 13, flexShrink: 0, color: t.text }}>✦</div>
                <div style={{ background: t.bubbleBot, border: `1px solid ${t.bubbleBotBorder}`, borderRadius: "4px 14px 14px 14px", padding: "14px 18px", display: "flex", gap: 5, alignItems: "center" }}>
                  {[0, 0.2, 0.4].map((d, i) => (
                    <span key={i} style={{ width: 7, height: 7, borderRadius: "50%", background: t.subText, display: "inline-block", animation: `bounce 1.2s ${d}s infinite` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* INPUT BAR */}
      <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, background: t.bg, padding: "12px 1rem 16px", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, borderTop: `1px solid ${t.navBorder}`, transition: "background 0.3s, border-color 0.3s" }}>
        <div style={{ display: "flex", alignItems: "center", background: t.inputBg, border: `1.5px solid ${t.inputBorder}`, borderRadius: 12, padding: "6px 6px 6px 18px", width: "100%", maxWidth: 760, gap: 8, transition: "background 0.3s, border-color 0.3s" }}>
          <input
            style={{ flex: 1, border: "none", background: "transparent", fontFamily: "inherit", fontSize: 15, color: t.text, outline: "none" }}
            placeholder="Ask anything about MIT Faculty..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            style={{ width: 40, height: 40, borderRadius: 9, background: t.sendBtn, color: t.sendBtnText, border: "none", fontSize: 16, cursor: input.trim() ? "pointer" : "default", display: "grid", placeItems: "center", flexShrink: 0, opacity: input.trim() ? 1 : 0.35, transition: "opacity 0.2s, background 0.3s" }}
          >➤</button>
        </div>
        <p style={{ fontSize: 12, color: t.disclaimer, textAlign: "center", transition: "color 0.3s" }}>AI can make mistakes. Please verify important information.</p>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-5px); }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        input::placeholder { color: #999; }
        body { margin: 0; }
      `}</style>
    </div>
  );
}

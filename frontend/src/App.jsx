import { useState } from "react";
import "./App.css";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

const API = "http://localhost:8000";

function langFor(path) {
  const ext = path.split(".").pop().toLowerCase();
  const map = {
    py: "python", js: "javascript", jsx: "jsx", ts: "typescript",
    tsx: "tsx", json: "json", md: "markdown", html: "html",
    css: "css", c: "c", h: "c", cpp: "cpp", java: "java",
    go: "go", rs: "rust", rb: "ruby", sh: "bash", yml: "yaml",
    yaml: "yaml", toml: "toml", rst: "markup", pyi: "python",
  };
  return map[ext] || "text";
}

export default function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [indexedUrl, setIndexedUrl] = useState("");
  const [indexing, setIndexing] = useState(false);
  const [info, setInfo] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const [openSource, setOpenSource] = useState(null);

  async function analyze() {
    setError("");
    setInfo("");
    if (!repoUrl.trim()) return setError("Please enter a GitHub repo link");
    setIndexing(true);
    try {
      const res = await fetch(`${API}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ingest failed");
      setIndexedUrl(repoUrl.trim());
      setMessages([]);
      setInfo(`Indexed ${data.chunks_stored} chunks in ${data.seconds}s`);
    } catch (e) {
      setError(e.message);
    } finally {
      setIndexing(false);
    }
  }

  async function ask() {
    setError("");
    const q = question.trim();
    if (!q) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    setAsking(true);
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: indexedUrl, question: q }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ask failed");
      setMessages((m) => [
        ...m,
        { role: "bot", text: data.answer, sources: data.sources },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app">
      <h1>RepoMentor</h1>
      <p className="sub">Ask questions about any GitHub repo</p>

      <div className="row">
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          disabled={indexing}
        />
        <button onClick={analyze} disabled={indexing}>
          {indexing ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {info && <p className="info">{info}</p>}
      {error && <p className="error">{error}</p>}

      {indexedUrl && (
        <>
          <div className="chat">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div className="text">{m.text}</div>
                {m.sources && m.sources.length > 0 && (
                  <div className="sources">
                    {m.sources.map((s, j) => {
                      const key = `${i}-${j}`;
                      return (
                        <div key={j}>
                          <button
                            className="src"
                            onClick={() =>
                              setOpenSource(openSource === key ? null : key)
                            }
                          >
                            {s.file_path}:{s.start_line}-{s.end_line}
                          </button>
                          {openSource === key && (
                            <SyntaxHighlighter
                              language={langFor(s.file_path)}
                              style={vscDarkPlus}
                              showLineNumbers
                              startingLineNumber={s.start_line}
                              customStyle={{
                                margin: 0,
                                borderRadius: 6,
                                fontSize: 12,
                                maxHeight: 300,
                              }}
                            >
                              {s.snippet}
                            </SyntaxHighlighter>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
            {asking && <div className="msg bot">Thinking...</div>}
          </div>

          <div className="row">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !asking && ask()}
              placeholder="Ask a question about this repo"
              disabled={asking}
            />
            <button onClick={ask} disabled={asking}>
              Ask
            </button>
          </div>
        </>
      )}
    </div>
  );
}
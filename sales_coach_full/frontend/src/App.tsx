import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Play, Brain, Loader2 } from "lucide-react";
import type { Persona } from "./lib/api";
import { getPersonas, createSession, sendMessage, uploadAudio, endSession, health } from "./lib/api";
import { MicButton } from "./components/MicButton";

function clsx(...xs: Array<string | false | undefined>) {
  return xs.filter(Boolean).join(" ");
}

export default function App() {
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaKey, setPersonaKey] = useState<string>("");
  const [sessionId, setSessionId] = useState<string>("");
  const [agentId, setAgentId] = useState<string>("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; text: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [ending, setEnding] = useState(false);
  const [analysis, setAnalysis] = useState<{ analysis?: unknown; openai_analysis?: unknown } | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const h = await health();
        setApiOk(h.status === "ok");
      } catch {
        setApiOk(false);
      }
      try {
        const ps = await getPersonas();
        setPersonas(ps);
        if (ps.length) setPersonaKey(ps[0].key);
      } catch {
        // noop
      }
    })();
  }, []);

  const canStart = useMemo(() => !!personaKey && apiOk, [personaKey, apiOk]);

  async function onStart() {
    if (!canStart) return;
    setLoading(true);
    try {
      const { session_id, agent_id } = await createSession(personaKey);
      setSessionId(session_id);
      setAgentId(agent_id);
      setMessages([]);
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }

  async function onSend() {
    if (!sessionId || !input.trim()) return;
    const text = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "rep", text }]);
    setLoading(true);
    try {
      const { reply_text } = await sendMessage(sessionId, text);
      setMessages((m) => [...m, { role: "customer", text: reply_text }]);
    } finally {
      setLoading(false);
    }
  }

  async function onUpload(blob: Blob) {
    if (!sessionId || !blob) return;
    setUploading(true);
    try {
      const { transcript, reply_text } = await uploadAudio(sessionId, blob);
      setMessages((m) => [...m, { role: "rep", text: transcript }, { role: "customer", text: reply_text }]);
    } finally {
      setUploading(false);
    }
  }

  async function onEnd() {
    if (!sessionId) return;
    setEnding(true);
    try {
      const data = await endSession(sessionId);
      setAnalysis(data);
    } finally {
      setEnding(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 backdrop-blur bg-neutral-900/80 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-4">
          <div className="flex-1">
            <h1 className="text-xl font-semibold tracking-tight">Sales Coach</h1>
            <p className="text-sm text-neutral-400">Minimal, clean, animated UI</p>
          </div>
          <div className={clsx("text-xs px-2 py-1 rounded-full", apiOk ? "bg-green-500/20 text-green-300" : "bg-red-500/20 text-red-300")}>{apiOk ? "API Healthy" : apiOk === null ? "Checking..." : "API Down"}</div>
        </div>
      </header>

      <main className="flex-1">
        <div className="max-w-5xl mx-auto px-4 py-8">
          {/* Start Panel */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="bg-neutral-800 rounded-2xl shadow-lg p-4 md:p-6">
            <div className="grid gap-4 md:grid-cols-3 items-end">
              <div className="md:col-span-1">
                <label className="text-sm text-neutral-400">Persona</label>
                <select
                  className="mt-1 w-full bg-neutral-900 border border-white/10 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                  value={personaKey}
                  onChange={(e) => setPersonaKey(e.target.value)}
                >
                  {personas.map((p) => (
                    <option key={p.key} value={p.key}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2 flex items-end gap-3">
                <button
                  onClick={onStart}
                  disabled={!canStart || loading}
                  className={clsx(
                    "inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 text-white font-medium",
                    "disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:brightness-110 transition"
                  )}
                >
                  <Brain size={18} />
                  {loading ? "Starting..." : sessionId ? "Restart Session" : "Start Session"}
                </button>
                <AnimatePresence>
                  {sessionId && (
                    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }}>
                      <span className="text-xs text-neutral-400">Session: {sessionId}</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>

          {/* Chat Panel */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05, duration: 0.3 }} className="bg-neutral-800 rounded-2xl shadow-lg mt-6">
            <div className="p-4 border-b border-white/10 flex items-center gap-2">
              <div className="text-sm text-neutral-400">Agent: <span className="text-white/90">{agentId || "—"}</span></div>
            </div>
            <div className="h-[48vh] overflow-y-auto p-4 space-y-3">
              <AnimatePresence initial={false}>
                {messages.map((m, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    className={clsx(
                      "max-w-[80%] px-4 py-3 rounded-2xl",
                      m.role === "rep"
                        ? "bg-indigo-500/20 text-white ml-auto rounded-br-md"
                        : "bg-white/10 text-white/90 mr-auto rounded-bl-md"
                    )}
                  >
                    <div className="text-[11px] uppercase tracking-wide opacity-70 mb-1">{m.role}</div>
                    <div className="whitespace-pre-wrap leading-relaxed">{m.text}</div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {(loading || uploading) && (
                <div className="flex items-center gap-2 text-sm text-neutral-400">
                  <Loader2 className="animate-spin" size={16} />
                  {uploading ? "Processing audio..." : "Thinking..."}
                </div>
              )}
            </div>

            <div className="p-4 border-t border-white/10 flex items-center gap-2">
              <input
                type="text"
                className="flex-1 bg-neutral-900 border border-white/10 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Type a message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") onSend();
                }}
                disabled={!sessionId}
              />
              <MicButton sessionId={sessionId} onChunkUpload={onUpload} />
              <button
                onClick={onSend}
                disabled={!sessionId || !input.trim() || loading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={18} />
                Send
              </button>
            </div>
          </motion.div>

          {/* Analysis Panel */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.3 }} className="bg-neutral-800 rounded-2xl shadow-lg mt-6 p-4">
            <div className="flex items-center gap-3">
              <button
                onClick={onEnd}
                disabled={!sessionId || ending}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition disabled:opacity-50"
              >
                <Play size={18} /> Analyze & End Session
              </button>
              {analysis && <span className="text-sm text-neutral-400">Analysis received</span>}
            </div>
            {analysis && (
              <div className="mt-4 grid md:grid-cols-2 gap-4">
                <pre className="bg-black/40 rounded-lg p-3 overflow-auto max-h-64 text-xs">{JSON.stringify(analysis.analysis ?? analysis, null, 2)}</pre>
                <pre className="bg-black/40 rounded-lg p-3 overflow-auto max-h-64 text-xs">{JSON.stringify(analysis.openai_analysis ?? null, null, 2)}</pre>
              </div>
            )}
          </motion.div>
        </div>
      </main>

      <footer className="border-t border-white/10 py-6 text-center text-xs text-neutral-400">Built with React + Vite + Tailwind + framer-motion</footer>
    </div>
  );
}

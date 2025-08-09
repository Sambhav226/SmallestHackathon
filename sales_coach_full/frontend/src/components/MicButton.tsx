import { useEffect, useMemo, useRef, useState } from "react";
import { Mic, Square } from "lucide-react";
import { MicRecorder } from "../lib/recorder";

export function MicButton({ sessionId, onChunkUpload }: { sessionId: string; onChunkUpload: (blob: Blob) => Promise<any> | void }) {
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [bufferedMode, setBufferedMode] = useState(true);
  const recorderRef = useRef<MicRecorder | null>(null);

  useEffect(() => {
    if (!recording) return;
    const rec = new MicRecorder();
    recorderRef.current = rec;
    if (bufferedMode) {
      rec.startBuffered(async (blob) => {
        if (!sessionId) return;
        setBusy(true);
        try {
          await onChunkUpload(blob);
        } finally {
          setBusy(false);
        }
      }).catch(() => setRecording(false));
    } else {
      rec.start(async (blob) => {
        if (!sessionId) return;
        if (busy) return;
        setBusy(true);
        try {
          await onChunkUpload(blob);
        } finally {
          setBusy(false);
        }
      }).catch(() => setRecording(false));
    }
    return () => rec.stop();
  }, [recording, sessionId, bufferedMode]);

  const canRecord = useMemo(() => !!sessionId && !busy, [sessionId, busy]);

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setRecording((r) => !r)}
        disabled={!canRecord}
        className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition disabled:opacity-50"
        title={recording ? "Stop" : "Record"}
      >
        {recording ? <Square size={18} /> : <Mic size={18} />}
        {recording ? "Stop" : "Record"}
      </button>
      <label className="text-xs text-neutral-400 inline-flex items-center gap-1">
        <input type="checkbox" checked={bufferedMode} onChange={(e) => setBufferedMode(e.target.checked)} />
        buffered
      </label>
    </div>
  );
} 
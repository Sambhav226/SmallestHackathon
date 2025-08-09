import { useEffect, useMemo, useRef, useState } from "react";
import { Mic, Square } from "lucide-react";
import { MicRecorder } from "../lib/recorder";

export function MicButton({ sessionId, onChunkUpload }: { sessionId: string; onChunkUpload: (blob: Blob) => Promise<any> | void }) {
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const recorderRef = useRef<MicRecorder | null>(null);

  useEffect(() => {
    if (!recording) return;
    const rec = new MicRecorder();
    recorderRef.current = rec;
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
    return () => rec.stop();
  }, [recording, sessionId]);

  const canRecord = useMemo(() => !!sessionId && !busy, [sessionId, busy]);

  return (
    <button
      onClick={() => setRecording((r) => !r)}
      disabled={!canRecord}
      className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition disabled:opacity-50"
      title={recording ? "Stop" : "Record"}
    >
      {recording ? <Square size={18} /> : <Mic size={18} />}
      {recording ? "Stop" : "Record"}
    </button>
  );
} 
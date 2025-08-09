import axios from "axios";

const baseURL = (import.meta as ImportMeta).env?.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL,
});

export type Persona = { key: string; name: string };

export async function getPersonas(): Promise<Persona[]> {
  const { data } = await api.get<{ personas: Persona[] }>("/personas");
  return data.personas;
}

export async function health(): Promise<{ status: string }> {
  const { data } = await api.get("/health");
  return data;
}

export async function createSession(personaKey: string): Promise<{ session_id: string; agent_id: string }> {
  const { data } = await api.post("/sessions", { persona_key: personaKey });
  return data;
}

export async function sendMessage(sessionId: string, text: string): Promise<{ reply_text: string; tts_base64: string }> {
  const { data } = await api.post(`/sessions/${encodeURIComponent(sessionId)}/message`, { text });
  return data;
}

export async function uploadAudio(
  sessionId: string,
  fileOrBlob: Blob
): Promise<{ transcript: string; reply_text: string; tts_base64: string }> {
  const form = new FormData();
  const f = fileOrBlob instanceof File ? fileOrBlob : new File([fileOrBlob], "chunk.webm", { type: fileOrBlob.type || "audio/webm" });
  form.append("file", f);
  const { data } = await api.post(`/sessions/${encodeURIComponent(sessionId)}/upload_audio`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function endSession(sessionId: string): Promise<{ analysis: unknown; openai_analysis: unknown }> {
  const { data } = await api.post(`/sessions/${encodeURIComponent(sessionId)}/end`);
  return data;
} 
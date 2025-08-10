# FastAPI app wiring updated to include audio upload (STT) endpoint and OpenAI analysis option
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
# from os.path import abspath, dirname, join
# PARENT_DIR = abspath(join(dirname(__file__), '..'))
# if PARENT_DIR not in sys.path:
#     sys.path.insert(0, PARENT_DIR)
from smallest_wrapper import SmallestClientWrapper
from session_manager import SessionManager
from personas import PERSONAS
from stt import transcribe_audio_deepgram
from analysis import analyze_with_openai
from reply import generate_reply_text

class CreateSessionReq(BaseModel):
    persona_key: str

class MessageReq(BaseModel):
    text: str

SMALLEST_API_KEY = os.environ.get("SMALLEST_API_KEY")
app = FastAPI(title="Sales Coach Backend")

# Enable CORS for local frontend dev
frontend_origins = [
    os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173"),
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Require real Smallest.ai SDK and API key
smallest = SmallestClientWrapper(api_key=SMALLEST_API_KEY)
session_mgr = SessionManager(smallest)

@app.get("/personas")
def list_personas():
    return {"personas": [{"key": k, "name": v["name"]} for k, v in PERSONAS.items()]}

@app.post("/sessions")
def create_session(req: CreateSessionReq):
    if req.persona_key not in PERSONAS:
        raise HTTPException(status_code=400, detail="unknown persona_key")
    session_id, agent_id = session_mgr.create_session(req.persona_key)
    return {"session_id": session_id, "agent_id": agent_id}

@app.post("/sessions/{session_id}/message")
def send_message(session_id: str, msg: MessageReq):
    try:
        reply_text, tts_b64 = session_mgr.send_rep_message(session_id, msg.text)
        return {"reply_text": reply_text, "tts_base64": tts_b64}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/sessions/{session_id}/upload_audio")
async def upload_audio(session_id: str, file: UploadFile = File(...)):
    # Accepts an audio file from the frontend and returns transcription
    if session_id not in session_mgr.sessions:
        raise HTTPException(status_code=404, detail="session not found")
    content = await file.read()
    transcript = transcribe_audio_deepgram(content, filename=file.filename)
    # store as rep message (assumes rep spoke)
    session_mgr.sessions[session_id]['messages'].append({'role':'rep','text': transcript})
    # Now attempt agent reply (optional)
    agent_id = session_mgr.sessions[session_id]['agent_id']
    reply = ""
    tts_b64 = ""
    try:
        reply = smallest.converse_text(agent_id, transcript)
        if reply:
            session_mgr.sessions[session_id]['messages'].append({'role':'customer','text':reply})
            try:
                tts_b64 = smallest.synthesize_tts_base64(reply)
            except Exception:
                tts_b64 = ""
    except Exception:
        reply = ""
        tts_b64 = ""
    return {'transcript': transcript, 'reply_text': reply, 'tts_base64': tts_b64}

@app.post("/voice/{session_id}")
async def voice_exchange(session_id: str, file: UploadFile = File(...)):
    if session_id not in session_mgr.sessions:
        raise HTTPException(status_code=404, detail="session not found")
    content = await file.read()
    transcript = transcribe_audio_deepgram(content, filename=file.filename)
    # Append transcript
    session_mgr.sessions[session_id]['messages'].append({'role': 'rep', 'text': transcript})
    # Produce a reply text (OpenAI if available, else heuristic) and TTS
    agent_id = session_mgr.sessions[session_id]['agent_id']
    persona_key = session_mgr.sessions[session_id]['persona_key']
    persona = PERSONAS.get(persona_key, {})
    reply_text = generate_reply_text(session_mgr.sessions[session_id]['messages'], persona.get('prompt', ''))
    tts_b64 = smallest.synthesize_tts_base64(reply_text)
    session_mgr.sessions[session_id]['messages'].append({'role': 'customer', 'text': reply_text})
    return { 'transcript': transcript, 'reply_text': reply_text, 'tts_base64': tts_b64 }

@app.post("/sessions/{session_id}/end")
def end_session(session_id: str):
    if session_id not in session_mgr.sessions:
        raise HTTPException(status_code=404, detail="session not found")
    coaching = session_mgr.end_and_analyze(session_id)
    # attempt OpenAI analysis if key present
    full_transcript = coaching.get('transcript','')
    openai_result = analyze_with_openai(full_transcript)
    return {"analysis": coaching, "openai_analysis": openai_result}

@app.get("/health")
def health():
    return {"status": "ok"}

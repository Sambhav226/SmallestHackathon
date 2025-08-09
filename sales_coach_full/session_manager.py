import uuid
from smallest_wrapper import SmallestClientWrapper
from personas import PERSONAS
from analysis import analyze_conversation_heuristic
import os

class SessionManager:
    def __init__(self, smallest_wrapper=None):
        self.smallest = smallest_wrapper or SmallestClientWrapper(force_mock=True)
        self.sessions = {}

    def create_session(self, persona_key):
        if persona_key not in PERSONAS:
            raise ValueError("Unknown persona key")
        persona = PERSONAS[persona_key]
        resp = self.smallest.create_agent(display_name=persona["name"], persona_prompt=persona["prompt"])
        agent_id = resp.get("agent_id")
        session_id = "sess_" + uuid.uuid4().hex[:8]
        self.sessions[session_id] = {"agent_id": agent_id, "persona_key": persona_key, "messages": []}
        return session_id, agent_id

    def send_rep_message(self, session_id, text):
        if session_id not in self.sessions:
            raise ValueError("session not found")
        session = self.sessions[session_id]
        agent_id = session["agent_id"]
        session["messages"].append({"role": "rep", "text": text})
        reply = self.smallest.converse_text(agent_id, text)
        session["messages"].append({"role": "customer", "text": reply})
        tts_b64 = self.smallest.synthesize_tts_base64(reply)
        return reply, tts_b64

    def end_and_analyze(self, session_id):
        if session_id not in self.sessions:
            raise ValueError("session not found")
        session = self.sessions[session_id]
        coaching = analyze_conversation_heuristic(session["messages"])
        session["analysis"] = coaching
        return coaching

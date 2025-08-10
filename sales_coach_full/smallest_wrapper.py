import os, sys, uuid, random, json

class SmallestClientWrapper:
    def __init__(self, api_key=None, force_mock=False):
        self.api_key = api_key or os.environ.get("SMALLEST_API_KEY")
        if not self.api_key:
            raise RuntimeError("SMALLEST_API_KEY not set")
        try:
            # Use Atoms with explicit Configuration taking access_token from env/key
            from smallestai.atoms.atoms_client import AtomsClient  # type: ignore
            from smallestai.atoms.configuration import Configuration  # type: ignore
            from smallestai.waves.waves_client import WavesClient  # type: ignore

            atoms_config = Configuration(access_token=self.api_key)
            self.atoms_client = AtomsClient(configuration=atoms_config)
            # WavesClient accepts api_key directly
            self.waves_client = WavesClient(api_key=self.api_key)
        except Exception as e:
            raise RuntimeError(f"smallestai SDK not available or failed to import: {e}")

    def create_agent(self, display_name, persona_prompt, voice_config=None):
        # Build request model per SDK
        try:
            from smallestai.atoms.models.create_agent_request import CreateAgentRequest  # type: ignore
            req = CreateAgentRequest(name=display_name, global_prompt=persona_prompt)
            resp = self.atoms_client.create_agent(req)
            # Normalize id from response model/dict
            agent_id = None
            # pydantic models: try attributes first
            for attr in ["id", "agent_id"]:
                if hasattr(resp, attr):
                    agent_id = getattr(resp, attr)
                    break
            if agent_id is None and hasattr(resp, "data"):
                data = getattr(resp, "data")
                if isinstance(data, dict):
                    agent_id = data.get("id") or data.get("agent_id")
                else:
                    for attr in ["id", "agent_id"]:
                        if hasattr(data, attr):
                            agent_id = getattr(data, attr)
                            break
            return {"agent_id": agent_id or "agent-created"}
        except Exception as e:
            raise RuntimeError(f"create_agent_failed: {e}")

    def converse_text(self, agent_id, user_message):
        # Temporary text reply fallback until a chat endpoint is available via SDK.
        # Keeps the pipeline working so TTS can be produced by Waves.
        if not user_message:
            return "I didn't catch that. Could you please repeat?"
        trimmed = user_message.strip()
        if len(trimmed) > 400:
            trimmed = trimmed[:400] + "…"
        return f"You said: {trimmed}"

    def synthesize_tts_base64(self, text, voice_id=None):
        if voice_id is None:
            voice_id = os.environ.get("SMALLEST_VOICE_ID") or None
        resp = self.waves_client.synthesize(text=text, voice_id=voice_id)
        if isinstance(resp, bytes):
            import base64
            return base64.b64encode(resp).decode('utf-8')
        if isinstance(resp, dict):
            audio_b64 = resp.get('audio') or resp.get('data')
            if isinstance(audio_b64, bytes):
                import base64
                return base64.b64encode(audio_b64).decode('utf-8')
            return audio_b64
        return str(resp)

    def delete_agent(self, agent_id: str) -> None:
        try:
            self.atoms_client.delete_agent(id=agent_id)
        except Exception as e:
            raise RuntimeError(f"delete_agent_failed: {e}")

if __name__ == '__main__':
    print('SmallestClientWrapper module loaded')

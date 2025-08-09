import os, sys, uuid, random, json

class MockSmallestClient:
    def __init__(self):
        self.agents = {}

    def create_agent(self, display_name, persona_prompt, voice_config=None):
        agent_id = "mock_agent_" + uuid.uuid4().hex[:8]
        self.agents[agent_id] = {
            "display_name": display_name,
            "prompt": persona_prompt,
            "voice_config": voice_config or {}
        }
        return {"agent_id": agent_id}

    def converse_text(self, agent_id, user_message):
        agent = self.agents.get(agent_id, {})
        prompt = agent.get("prompt", "")
        if "skeptic" in prompt.lower():
            options = [
                "Hmm... how do I know that's true?",
                "That's a big claim. Any proof?",
                "Short answer: not convinced."
            ]
            return random.choice(options)
        if "price" in prompt.lower() or "budget" in prompt.lower():
            options = [
                "What's the final price?",
                "Are there discounts?",
                "I can buy a cheaper one elsewhere."
            ]
            return random.choice(options)
        if "technical" in prompt.lower() or "specification" in prompt.lower():
            options = [
                "What's the exact battery capacity (mAh)?",
                "Can you give me the benchmark numbers?",
                "What's the range in km?"
            ]
            return random.choice(options)
        if "emotional" in prompt.lower() or "testimonial" in prompt.lower():
            options = [
                "Does anyone I know use this?",
                "I want to hear a story of someone who loved it.",
                "How will this make my life better?"
            ]
            return random.choice(options)
        if "delay" in prompt.lower() or "think about" in prompt.lower():
            options = [
                "I'll think about it and get back to you.",
                "Maybe next month.",
                "Not sure — call me later."
            ]
            return random.choice(options)
        return "Okay. Tell me more."

    def synthesize_tts_base64(self, text, voice_id=None):
        fake_b64 = ("BASE64_AUDIO_" + uuid.uuid4().hex)[:120]
        return fake_b64

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
        # The Atoms SDK does not expose a simple text chat endpoint in this package.
        # Raise a clear error so the API does not silently mock.
        raise RuntimeError("Text conversation is not supported via AtomsClient SDK in this build. Implement a conversation endpoint or remove this feature.")

    def synthesize_tts_base64(self, text, voice_id=None):
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

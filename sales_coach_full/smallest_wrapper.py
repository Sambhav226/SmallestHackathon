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
        self.force_mock = force_mock
        self._use_mock = force_mock
        self._client = None

        if not self._use_mock:
            try:
                # Try to import official SDK
                from smallestai.atoms import AtomsClient  # type: ignore
                from smallestai.waves import WavesClient  # type: ignore
                # instantiate real clients
                self.atoms_client = AtomsClient(api_key=self.api_key)
                self.waves_client = WavesClient(api_key=self.api_key)
                self._use_mock = False
                self._client = None
            except Exception as e:
                print("smallestai SDK not available or failed to import; using Mock client.", file=sys.stderr)
                self._use_mock = True
                self._client = MockSmallestClient()
        else:
            self._use_mock = True
            self._client = MockSmallestClient()

    def create_agent(self, display_name, persona_prompt, voice_config=None):
        if self._use_mock:
            return self._client.create_agent(display_name, persona_prompt, voice_config)
        else:
            # Real SDK call: create an agent using AtomsClient
            # The exact payload keys may vary with SDK version; refer to Smallest.ai docs.
            payload = {
                "display_name": display_name,
                "globalPrompt": persona_prompt,
            }
            if voice_config:
                payload["synthesizer"] = {"voiceConfig": voice_config}
            try:
                resp = self.atoms_client.create_agent(payload)
                # depending on SDK, resp may have different shape; normalize
                agent_id = None
                if isinstance(resp, dict):
                    agent_id = resp.get('id') or resp.get('agent_id') or resp.get('data', {}).get('id')
                return {"agent_id": agent_id or 'real-agent-created'}
            except Exception as e:
                # fallback
                return {"agent_id": 'real-agent-placeholder', "error": str(e)}

    def converse_text(self, agent_id, user_message):
        if self._use_mock:
            return self._client.converse_text(agent_id, user_message)
        else:
            try:
                # Call the Atoms converse endpoint
                # The SDK often provides a 'converse' or 'chat' method. Example:
                resp = self.atoms_client.converse(agent_id=agent_id, input={"type":"text","text":user_message})
                # Extract text from response
                if isinstance(resp, dict):
                    # Try several common fields
                    for key in ['output', 'message', 'text', 'reply']:
                        if key in resp:
                            return resp[key]
                    # Deeply check typical nested structures
                    if 'choices' in resp and len(resp['choices'])>0:
                        ch = resp['choices'][0]
                        return ch.get('message', {}).get('content') or ch.get('text') or str(ch)
                return str(resp)
            except Exception as e:
                return f"[converse_error] {e}"

    def synthesize_tts_base64(self, text, voice_id=None):
        if self._use_mock:
            return self._client.synthesize_tts_base64(text, voice_id=voice_id)
        else:
            try:
                # Use WavesClient to synthesize speech synchronously and return base64 audio
                # The Waves SDK typically exposes a synthesize or tts method.
                resp = self.waves_client.synthesize(text=text, voice_id=voice_id)
                # resp might be bytes or dict containing 'audio'
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
            except Exception as e:
                return f"[tts_error] {e}"

if __name__ == '__main__':
    print('SmallestClientWrapper module loaded')

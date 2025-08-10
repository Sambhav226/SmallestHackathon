import os, random
from typing import List, Dict

SYSTEM_PROMPT = "You are a concise, natural-sounding customer speaking in short sentences."

CANNED_REPLIES = [
    "Can you clarify that?",
    "What does that mean for me?",
    "I'm not sure. Could you explain simply?",
    "What would be the total cost?",
    "How long would that take?",
    "Do you have any proof or examples?",
    "What are the trade-offs?",
]

KEYWORD_REPLIES = [
    ("price|cost|discount", ["Is there a discount?", "What's the final price?", "Any additional fees?"]),
    ("battery|range|capacity", ["What's the actual range?", "How long does the battery last?", "What capacity is it?"]),
    ("delivery|shipping|time", ["How long is delivery?", "When can I get it?", "Is shipping included?"]),
    ("warranty|support", ["What's the warranty?", "What support do you offer?", "Is support 24/7?"]),
]

def generate_reply_text(messages: List[Dict[str, str]], persona_prompt: str = "") -> str:
    """
    messages: list of {role: 'rep'|'customer', text: str}
    persona_prompt: optional string to bias the customer style
    """
    last_rep = next((m["text"] for m in reversed(messages) if m.get("role") == "rep"), "")

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            user_prompt = (
                f"Persona: {persona_prompt}\n"
                f"Conversation so far (latest from rep):\n{last_rep}\n\n"
                "Reply as the customer in one or two short sentences."
            )
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=120,
                temperature=0.7,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    txt = last_rep.lower()
    for pattern, replies in KEYWORD_REPLIES:
        import re
        if re.search(pattern, txt):
            return random.choice(replies)
    return random.choice(CANNED_REPLIES) 
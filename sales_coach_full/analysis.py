import os, json
from typing import List, Dict, Any
from analysis_heuristic import analyze_conversation_heuristic

def analyze_with_openai(transcript: str) -> Dict[str, Any]:
    """If OPENAI_API_KEY is present, call OpenAI's chat completion to analyze.
    Otherwise fall back to heuristic analysis and return a structured dict.
    Note: this function uses the openai package when available; real calls will
    only work when OPENAI_API_KEY is set in your environment and the package
    is installed.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        # fallback to heuristic (need to convert transcript to messages list)
        messages = []
        for line in transcript.splitlines():
            if line.strip().startswith('rep:'):
                messages.append({'role':'rep', 'text': line.split(':',1)[1].strip()})
            elif line.strip().startswith('customer:'):
                messages.append({'role':'customer', 'text': line.split(':',1)[1].strip()})
            else:
                # try simple parse
                parts = line.split(':',1)
                if len(parts) == 2:
                    messages.append({'role': parts[0].strip(), 'text': parts[1].strip()})
        return analyze_conversation_heuristic(messages)

    # Real OpenAI call placeholder
    try:
        import openai
        openai.api_key = api_key
        prompt = f"Analyze the following transcript and produce json with scores, improvements, missed_facts, rewrites.\n\n{transcript}"
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role':'system','content':'You are an expert sales coach.'}, {'role':'user','content':prompt}],
            max_tokens=800
        )
        text = resp['choices'][0]['message']['content']
        # attempt to parse JSON out of response
        try:
            data = json.loads(text)
            return data
        except Exception:
            # if not JSON, wrap the text
            return {'raw': text}
    except Exception as e:
        return {'error': 'openai_call_failed', 'detail': str(e)}

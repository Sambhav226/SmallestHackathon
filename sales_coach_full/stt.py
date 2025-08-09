import os, requests, json

def _infer_content_type(filename: str) -> str:
    name = (filename or '').lower()
    if name.endswith('.wav'): return 'audio/wav'
    if name.endswith('.webm'): return 'audio/webm'
    if name.endswith('.mp3'): return 'audio/mpeg'
    if name.endswith('.m4a') or name.endswith('.mp4'): return 'audio/mp4'
    if name.endswith('.ogg') or name.endswith('.oga'): return 'audio/ogg'
    return 'application/octet-stream'

def transcribe_audio_deepgram(file_bytes: bytes, filename: str = 'audio.wav') -> str:
    """Transcribe audio using Deepgram REST API if DEEPGRAM_API_KEY is set.
    Returns transcript string. Fallback to configuration error if key is absent.
    """
    api_key = os.environ.get('DEEPGRAM_API_KEY')
    if not api_key:
        return "[configuration_error] Missing DEEPGRAM_API_KEY"
    url = 'https://api.deepgram.com/v1/listen'
    headers = {
        'Authorization': 'Token ' + api_key,
        'Content-Type': _infer_content_type(filename),
    }
    params = {
        # Prefer smart_format (punctuation, capitalization, numbers, dates, etc.)
        'smart_format': 'true',
        'model': os.environ.get('DEEPGRAM_MODEL', 'nova-2'),
    }
    try:
        # Use detect_language for auto language detection if not explicitly set via env
        dg_lang = os.environ.get('DEEPGRAM_LANGUAGE')
        if dg_lang:
            params['language'] = dg_lang
        else:
            params['detect_language'] = 'true'

        resp = requests.post(url, headers=headers, params=params, data=file_bytes, timeout=30)
        try:
            resp.raise_for_status()
        except requests.HTTPError as he:
            detail = ''
            try:
                detail = resp.text
            except Exception:
                pass
            return f"[deepgram_error] {he}: {detail}"
        data = resp.json()
        # navigate Deepgram response
        transcript = ''
        try:
            transcript = data.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript', '')
        except Exception:
            transcript = json.dumps(data)
        return transcript
    except Exception as e:
        return f"[deepgram_error] {e}"

def transcribe_audio_mock(file_bytes: bytes) -> str:
    return transcribe_audio_deepgram(file_bytes)

if __name__ == '__main__':
    print('stt module OK')

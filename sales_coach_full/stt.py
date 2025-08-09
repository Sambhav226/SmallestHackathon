import os, requests, json

def transcribe_audio_deepgram(file_bytes: bytes, filename: str = 'audio.wav') -> str:
    """Transcribe audio using Deepgram REST API if DEEPGRAM_API_KEY is set.
    Returns transcript string. Fallback to mock if key is absent.
    """
    api_key = os.environ.get('DEEPGRAM_API_KEY')
    if not api_key:
        return "[mock transcription] I am interested in battery and range."
    url = 'https://api.deepgram.com/v1/listen'
    headers = {
        'Authorization': 'Token ' + api_key,
        'Content-Type': 'application/octet-stream'
    }
    params = {
        'punctuate': True,
        'language': 'multi',
        'model': os.environ.get('DEEPGRAM_MODEL', 'nova-3')  # example default
    }
    try:
        resp = requests.post(url, headers=headers, params=params, data=file_bytes, timeout=30)
        resp.raise_for_status()
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

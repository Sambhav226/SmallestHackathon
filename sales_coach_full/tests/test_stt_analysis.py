import unittest
from stt import transcribe_audio_mock, transcribe_audio_deepgram
from analysis import analyze_with_openai
import os

class TestSTTAndAnalysis(unittest.TestCase):
    def test_mock_stt(self):
        txt = transcribe_audio_mock(b'fake')
        self.assertTrue(isinstance(txt, str))
        self.assertIn('battery', txt.lower())

    def test_deepgram_placeholder(self):
        # In this environment deepgram key not set; should return placeholder
        txt = transcribe_audio_deepgram(b'fake')
        self.assertTrue(isinstance(txt, str))

    def test_openai_fallback(self):
        # No OPENAI_API_KEY in environment here; analyze_with_openai should fallback to heuristic
        transcript = 'rep: Hello\ncustomer: What is the battery capacity?'
        res = analyze_with_openai(transcript)
        self.assertIn('scores', res)

if __name__ == '__main__':
    unittest.main()

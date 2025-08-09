import unittest
from session_manager import SessionManager
from smallest_wrapper import SmallestClientWrapper

class TestSessionManagerMock(unittest.TestCase):
    def setUp(self):
        self.wrapper = SmallestClientWrapper(force_mock=True)
        self.sm = SessionManager(self.wrapper)

    def test_create_session_and_flow(self):
        session_id, agent_id = self.sm.create_session('feature_engineer')
        self.assertTrue(session_id.startswith('sess_'))
        # send a rep message
        reply, tts = self.sm.send_rep_message(session_id, 'Hello, can I tell you about range and battery?')
        self.assertIsInstance(reply, str)
        self.assertTrue(tts.startswith('BASE64_AUDIO_'))
        # end and analyze
        analysis = self.sm.end_and_analyze(session_id)
        self.assertIn('scores', analysis)
        scores = analysis['scores']
        self.assertIn('rapport', scores)
        self.assertIn('product_knowledge', scores)

    def test_unknown_persona(self):
        with self.assertRaises(ValueError):
            self.sm.create_session('nonexistent_persona')

    def test_invalid_session(self):
        with self.assertRaises(ValueError):
            self.sm.send_rep_message('sess_invalid', 'hi')

if __name__ == '__main__':
    unittest.main()

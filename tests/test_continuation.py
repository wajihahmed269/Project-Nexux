import unittest
from unittest.mock import patch, MagicMock, call
from core.agent import Agent
from core.continuation import run_with_fallback

class TestContinuation(unittest.TestCase):

    def make_agent(self, role="coder"):
        return Agent(
            role=role,
            model="llama3-70b-8192",
            api_key="fake",
            api_url="https://fake.url"
        )

    @patch("core.continuation.save_checkpoint")
    @patch("core.continuation.update_step")
    @patch("core.continuation.log_event")
    @patch("core.agent.httpx.post")
    def test_primary_succeeds(self, mock_post, mock_log, mock_update, mock_cp):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": "primary output"}}],
                "usage": {"total_tokens": 100}
            }
        )
        agent = self.make_agent()
        result = run_with_fallback(agent, "do task", "t1", "1.1")
        self.assertEqual(result, "primary output")

    @patch("core.continuation.save_checkpoint")
    @patch("core.continuation.update_step")
    @patch("core.continuation.log_event")
    @patch("core.agent.httpx.post")
    def test_smart_retry_on_failure(self, mock_post, mock_log, mock_update, mock_cp):
        # First call fails, second (retry) succeeds
        fail_response = MagicMock(status_code=500, text="Server error")
        success_response = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": "retry output"}}],
                "usage": {"total_tokens": 80}
            }
        )
        mock_post.side_effect = [fail_response, success_response]
        agent = self.make_agent()
        result = run_with_fallback(agent, "do task", "t1", "1.1")
        self.assertEqual(result, "retry output")
        self.assertEqual(mock_post.call_count, 2)

if __name__ == "__main__":
    unittest.main()

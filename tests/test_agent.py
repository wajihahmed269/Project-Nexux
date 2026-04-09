import unittest
from unittest.mock import patch, MagicMock
from core.agent import Agent, AgentTimeoutError, AgentEmptyResponseError

class TestAgent(unittest.TestCase):

    def make_agent(self):
        return Agent(
            role="coder",
            model="llama3-70b-8192",
            api_key="fake-key",
            api_url="https://api.groq.com/openai/v1/chat/completions"
        )

    @patch("core.agent.httpx.post")
    def test_successful_run(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": "Hello!"}}],
                "usage": {"total_tokens": 50}
            }
        )
        agent = self.make_agent()
        result = agent.run("say hello")
        self.assertEqual(result, "Hello!")
        self.assertEqual(agent.status, "IDLE")
        self.assertEqual(agent.last_tokens, 50)

    @patch("core.agent.httpx.post")
    def test_empty_response_raises(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": ""}}],
                "usage": {"total_tokens": 10}
            }
        )
        agent = self.make_agent()
        with self.assertRaises(RuntimeError) as ctx:
            agent.run("say hello")
        self.assertIn("EMPTY", str(ctx.exception))
        self.assertEqual(agent.status, "FAILED")

    @patch("core.agent.httpx.post")
    def test_api_error_raises(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=429,
            text="Rate limit exceeded"
        )
        agent = self.make_agent()
        with self.assertRaises(RuntimeError) as ctx:
            agent.run("say hello")
        self.assertIn("API_ERROR", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()

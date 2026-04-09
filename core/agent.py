import httpx
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, role, model, api_key, api_url, backup=None, system_prompt=""):
        self.role = role
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.backup = backup
        self.system_prompt = system_prompt
        self.status = "IDLE"
        self.last_tokens = 0

    def run(self, prompt, context=""):
        self.status = "WORKING"
        parts = []
        if self.system_prompt:
            parts.append(self.system_prompt)
        if context:
            parts.append(context)
        parts.append(prompt)
        full_prompt = "\n\n".join(parts)
        
        try:
            content, tokens = self._call(full_prompt)
            self.status = "IDLE"
            self.last_tokens = tokens
            return content
        except Exception as e:
            self.status = "FAILED"
            raise RuntimeError(f"Agent {self.role} failed: {e}")

    def _call(self, prompt):
        response = httpx.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        
        return content, tokens

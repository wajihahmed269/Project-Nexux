import httpx

class AgentTimeoutError(Exception):
    pass

class AgentEmptyResponseError(Exception):
    pass

class AgentAPIError(Exception):
    pass

class Agent:
    def __init__(self, role, model, api_key, api_url, backup=None, system_prompt=""):
        self.role = role
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.backup = backup
        self.system_prompt = system_prompt
        tool_instructions = "\n\nIf you need to perform a web search to gather up-to-date or missing information, output EXACTLY this string and nothing else: [TOOL: WEB_SEARCH] \"your search query here\". Wait for the system to reply with the results before continuing."
        self.system_prompt += tool_instructions
        
        self.status = "IDLE"
        self.last_tokens = 0
        self.last_error = None

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
            self.last_error = None
            return content
        except AgentTimeoutError as e:
            self.status = "FAILED"
            self.last_error = ("TIMEOUT", str(e))
            raise RuntimeError(f"[TIMEOUT] Agent {self.role}: {e}")
        except AgentEmptyResponseError as e:
            self.status = "FAILED"
            self.last_error = ("EMPTY_RESPONSE", str(e))
            raise RuntimeError(f"[EMPTY] Agent {self.role}: {e}")
        except AgentAPIError as e:
            self.status = "FAILED"
            self.last_error = ("API_ERROR", str(e))
            raise RuntimeError(f"[API_ERROR] Agent {self.role}: {e}")
        except Exception as e:
            self.status = "FAILED"
            self.last_error = ("UNKNOWN", str(e))
            raise RuntimeError(f"[UNKNOWN] Agent {self.role}: {e}")

    def _call(self, prompt):
        try:
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
        except httpx.TimeoutException:
            raise AgentTimeoutError("Request timed out after 30s")
        except httpx.RequestError as e:
            raise AgentAPIError(f"Network error: {e}")

        if response.status_code != 200:
            raise AgentAPIError(f"HTTP {response.status_code}: {response.text[:200]}")

        data = response.json()
        
        if "gemini" in self.api_url:
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        else:
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            tokens = data.get("usage", {}).get("total_tokens", 0)

        if not content or not content.strip():
            raise AgentEmptyResponseError("Model returned empty response")

        return content, tokens

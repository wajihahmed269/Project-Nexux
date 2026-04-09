import os
from core.agent import Agent

agent = Agent(
    role="coder",
    model="llama3-70b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    api_url="https://api.groq.com/openai/v1/chat/completions"
)

print(agent.run("Say hello in one sentence."))
print(agent.status)

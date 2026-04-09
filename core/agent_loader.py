import yaml
import os
from core.agent import Agent

def load_prompt(role):
    path = f"prompts/{role}.txt"
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return ""

def load_agents():
    with open("agents/config.yaml") as f:
        config = yaml.safe_load(f)

    agents = {}
    for role, cfg in config["agents"].items():
        agents[role] = Agent(
            role=role,
            model=cfg["model"],
            api_key=os.getenv(cfg["api_key_env"]),
            api_url=cfg["api_url"],
            system_prompt=load_prompt(role)
        )
    return agents

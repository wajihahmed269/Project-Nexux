import yaml
import os
from core.agent import Agent

def load_prompt(role):
    # strip backup prefix — mistral_coder uses coder.txt
    base_role = role.split("_")[-1]
    path = f"prompts/{base_role}.txt"
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return ""

def load_agents():
    with open("agents/config.yaml") as f:
        config = yaml.safe_load(f)

    # First pass — create all agents without backups
    agents = {}
    for role, cfg in config["agents"].items():
        agents[role] = Agent(
            role=role,
            model=cfg["model"],
            api_key=os.getenv(cfg["api_key_env"]),
            api_url=cfg["api_url"],
            system_prompt=load_prompt(role)
        )

    # Second pass — wire backup references
    for role, cfg in config["agents"].items():
        backup_name = cfg.get("backup")
        if backup_name and backup_name in agents:
            agents[role].backup = agents[backup_name]

    return agents

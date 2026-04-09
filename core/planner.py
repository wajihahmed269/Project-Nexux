import json
import re
from core.memory import create_task
import uuid

PLANNER_PROMPT = """
You are a task planner for an AI orchestration system.
Break the user's task into clear steps. Return ONLY valid JSON, no markdown, no explanation.

Format:
{
  "phases": [
    {
      "phase": 1,
      "name": "phase name",
      "steps": [
        {"step_id": "1.1", "agent": "coder", "instruction": "what to do", "token_estimate": 500}
      ]
    }
  ],
  "total_token_estimate": 1500
}
"""

def plan_task(planner_agent, user_input):
    task_id = str(uuid.uuid4())[:8]
    response = planner_agent.run(user_input, context=PLANNER_PROMPT)
    
    # Safely extract JSON block
    match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
    if match:
        clean = match.group(1).strip()
    else:
        clean = response.strip()
        start = clean.find('{')
        end = clean.rfind('}')
        if start != -1 and end != -1:
            clean = clean[start:end+1]
            
    plan = json.loads(clean)
    
    task = create_task(task_id, user_input, plan)
    return task_id, plan

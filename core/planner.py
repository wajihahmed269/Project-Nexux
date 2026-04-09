import json
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
    
    # Strip markdown fences if model adds them
    clean = response.strip().strip("```json").strip("```").strip()
    plan = json.loads(clean)
    
    task = create_task(task_id, user_input, plan)
    return task_id, plan

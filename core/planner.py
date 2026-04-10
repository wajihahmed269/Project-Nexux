import json
import re
from core.memory import create_task
import uuid
from core.vector_memory import search_tasks

PLANNER_PROMPT = """
You are a task planner for an AI orchestration system.
Break the user's task into clear steps. Return ONLY valid JSON, no markdown, no explanation.

{past_context_prompt}

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
    
    # Query ChromaDB for past tasks to guide planning
    past_memory = search_tasks(user_input)
    if past_memory:
        past_context = f"Here is a successful plan from a similar past task. Use it as inspiration:\n{past_memory}"
    else:
        past_context = ""
        
    prompt = PLANNER_PROMPT.replace("{past_context_prompt}", past_context)
    
    response = planner_agent.run(user_input, context=prompt)
    
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

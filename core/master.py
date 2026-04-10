from core.memory import get_task, update_step, save_checkpoint
from core.logger import log_event
from core.continuation import run_with_fallback
from core.sandbox import extract_code, execute_code
from core.vector_memory import embed_task
import json

def run_task(task_id, agents, tracker=None):
    from core.scope_guard import ScopeGuard
    scope_guard = ScopeGuard()
    
    task = get_task(task_id)
    plan = task["plan"]
    context_accumulator = ""

    for phase in plan["phases"]:
        print(f"\n{'='*50}")
        print(f"Phase {phase['phase']}: {phase['name']}")
        print(f"{'='*50}")

        for step in plan_steps(phase):
            step_id = step["step_id"]
            agent_role = step["agent"]
            instruction = step["instruction"]

            print(f"\n  Step {step_id} → [{agent_role.upper()}]")
            print(f"  {instruction[:80]}...")

            update_step(task_id, step_id, "IN_PROGRESS")
            log_event(task_id, step_id, agent_role, "STARTED")

            agent = agents.get(agent_role)
            if not agent:
                log_event(task_id, step_id, agent_role, "FAILED",
                          "No agent configured for this role")
                update_step(task_id, step_id, "FAILED")
                continue

            if agent_role == "reviewer" and "```python" in context_accumulator:
                code = extract_code(context_accumulator.split("[Output from")[-1])
                if code:
                    sandbox_result = execute_code(code)
                    instruction += f"\n\n[SANDBOX EXECUTION LOG]:\n{sandbox_result}\n\nPlease review both the code string and this execution output."

            output = run_with_fallback(
                agent=agent,
                prompt=instruction,
                task_id=task_id,
                step_id=step_id,
                context=context_accumulator,
                tracker=tracker
            )

            if output:
                 context_accumulator += f"\n[Output from {agent_role} step {step_id}]:\n{output}\n"   # append to context
                 
            # ScopeGuard Token Check as requested in Day 19
            if tracker:
                scope_guard.check_tokens(tracker, task_id)

    print(f"\n{'='*50}")
    print(f"Task {task_id} complete.")
    print(f"{'='*50}\n")
    
    embed_task(task_id, task["user_input"], json.dumps(plan))

def plan_steps(phase):
    return phase.get("steps", [])

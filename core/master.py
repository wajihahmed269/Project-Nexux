from core.memory import get_task, update_step, save_checkpoint
from core.logger import log_event

def run_task(task_id, agents, tracker=None):
    task = get_task(task_id)
    plan = task["plan"]
    context_accumulator = ""   # carries all outputs from step to step

    for phase in plan["phases"]:
        print(f"\n--- Phase {phase['phase']}: {phase['name']} ---")
        for step in phase["steps"]:
            step_id = step["step_id"]
            agent_role = step["agent"]
            instruction = step["instruction"]

            log_event(task_id, step_id, agent_role, "STARTED")
            update_step(task_id, step_id, "IN_PROGRESS")

            agent = agents.get(agent_role)
            if not agent:
                update_step(task_id, step_id, "FAILED")
                log_event(task_id, step_id, agent_role, "FAILED", "No agent found")
                continue

            try:
                # Pass accumulated outputs as context
                output = agent.run(instruction, context=context_accumulator)
                update_step(task_id, step_id, "DONE", output)
                save_checkpoint(task_id, step_id, agent_role, output)
                
                if tracker:
                    tracker.record_step(task_id, step_id, agent.last_tokens)
                
                log_event(task_id, step_id, agent_role, "COMPLETED", f"{agent.last_tokens} tokens")
                context_accumulator += f"\n[Output from {agent_role} step {step_id}]:\n{output}\n"   # append to context
                
            except RuntimeError as e:
                update_step(task_id, step_id, "FAILED")
                log_event(task_id, step_id, agent_role, "FAILED", str(e))
                # Do not reset context_accumulator on failure so next steps might still proceed

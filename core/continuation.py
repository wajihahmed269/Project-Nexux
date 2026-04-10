from core.memory import update_step, save_checkpoint, load_checkpoint
from core.logger import log_event
from core.tools import web_search
import re

def _intercept_tools(output, agent, prompt, task_id, step_id, context):
    """Detect tool calls, execute them, and recursively prompt the agent."""
    if "[TOOL: WEB_SEARCH]" in output:
        match = re.search(r'\[TOOL:\s*WEB_SEARCH\]\s*"([^"]+)"', output)
        if match:
            query = match.group(1)
            print(f"\n  🔍 Agent initiated Web Search: '{query}'")
            search_result = web_search(query)
            tool_context = context + f"\n\n[System Tool Response for '{query}']:\n{search_result}"
            return agent.run("You previously requested a web search. Here are the true results. Now proceed to fully answer my original instruction:\n" + prompt, context=tool_context)
    return output

def build_retry_prompt(original_prompt, error_message, attempt_number):
    return f"""Previous attempt {attempt_number} failed with this error:
{error_message}

Analyze what went wrong and try again more carefully.

Original instruction:
{original_prompt}"""


def run_with_fallback(agent, prompt, task_id, step_id, context="", tracker=None):
    """
    Execution order:
    1. Primary agent — normal attempt
    2. Smart retry  — same agent, improved prompt with error context
    3. Backup agent — different model from config
    4. User intervention — skip / retry / cancel
    """

    # ── 1. Primary attempt ──────────────────────────────────────────────
    try:
        output = agent.run(prompt, context=context)
        output = _intercept_tools(output, agent, prompt, task_id, step_id, context)
        update_step(task_id, step_id, "DONE", output)
        save_checkpoint(task_id, step_id, agent.role, output)
        if tracker:
            tracker.record_step(task_id, step_id, agent.last_tokens)
        log_event(task_id, step_id, agent.role, "COMPLETED",
                  f"{agent.last_tokens} tokens")
        return output

    except RuntimeError as e:
        primary_error = str(e)
        error_type = agent.last_error[0] if agent.last_error else "UNKNOWN"
        log_event(task_id, step_id, agent.role, "FAILED",
                  f"Primary failed [{error_type}]: {primary_error}")

    # ── 2. Smart retry ───────────────────────────────────────────────────
    print(f"\n  ↻ Smart retry for step {step_id}...")
    retry_prompt = build_retry_prompt(prompt, primary_error, attempt_number=1)

    try:
        output = agent.run(retry_prompt, context=context)
        output = _intercept_tools(output, agent, retry_prompt, task_id, step_id, context)
        update_step(task_id, step_id, "DONE", output)
        save_checkpoint(task_id, step_id, agent.role, output)
        if tracker:
            tracker.record_step(task_id, step_id, agent.last_tokens)
        log_event(task_id, step_id, agent.role, "RETRIED",
                  f"Smart retry succeeded — {agent.last_tokens} tokens")
        print(f"  ✓ Smart retry succeeded")
        return output

    except RuntimeError as retry_error:
        log_event(task_id, step_id, agent.role, "FAILED",
                  f"Smart retry failed: {retry_error}")
        print(f"  ✗ Smart retry also failed")

    # ── 3. Backup agent ──────────────────────────────────────────────────
    if agent.backup:
        print(f"\n  ⚡ Handing off to backup agent: {agent.backup.role}...")
        log_event(task_id, step_id, agent.backup.role, "BACKUP_USED",
                  f"Primary {agent.role} exhausted")

        try:
            # Load last checkpoint for context if available
            checkpoint = load_checkpoint(task_id, step_id)
            backup_context = checkpoint["output"] if checkpoint else context

            output = agent.backup.run(prompt, context=backup_context)
            output = _intercept_tools(output, agent.backup, prompt, task_id, step_id, backup_context)
            update_step(task_id, step_id, "DONE", output)
            save_checkpoint(task_id, step_id, agent.backup.role, output)
            if tracker:
                tracker.record_step(task_id, step_id, agent.backup.last_tokens)
            log_event(task_id, step_id, agent.backup.role, "COMPLETED",
                      f"Backup succeeded — {agent.backup.last_tokens} tokens")
            print(f"  ✓ Backup agent succeeded")
            return output

        except RuntimeError as backup_error:
            log_event(task_id, step_id, agent.backup.role, "FAILED",
                      f"Backup also failed: {backup_error}")
            print(f"  ✗ Backup agent also failed")

    # ── 4. User intervention ─────────────────────────────────────────────
    return _ask_user(task_id, step_id, agent.role, prompt, context, agent,
                     tracker)


def _ask_user(task_id, step_id, agent_role, prompt, context, agent, tracker):
    log_event(task_id, step_id, agent_role, "USER_INTERVENED",
              "All fallbacks exhausted — asking user")

    print(f"\n  ⚠  Step {step_id} failed after all attempts.")
    print("  What would you like to do?")
    print("  [s] Skip this step and continue")
    print("  [r] Retry with your own modified instruction")
    print("  [c] Cancel the entire task")

    while True:
        choice = input("  Choice: ").strip().lower()

        if choice == "s":
            update_step(task_id, step_id, "SKIPPED")
            log_event(task_id, step_id, agent_role, "USER_INTERVENED",
                      "User skipped step")
            print(f"  → Step {step_id} skipped")
            return None

        elif choice == "r":
            new_instruction = input("  Enter your modified instruction: ").strip()
            try:
                output = agent.run(new_instruction, context=context)
                update_step(task_id, step_id, "DONE", output)
                save_checkpoint(task_id, step_id, agent_role, output)
                if tracker:
                    tracker.record_step(task_id, step_id, agent.last_tokens)
                log_event(task_id, step_id, agent_role, "COMPLETED",
                          "Succeeded after user retry")
                print(f"  ✓ User retry succeeded")
                return output
            except RuntimeError as e:
                print(f"  ✗ User retry also failed: {e}")
                print("  Falling back to skip/cancel...")
                continue

        elif choice == "c":
            log_event(task_id, step_id, agent_role, "USER_INTERVENED",
                      "User cancelled task")
            print("\n  Task cancelled by user.")
            raise SystemExit("Task cancelled")

        else:
            print("  Invalid choice. Enter s, r, or c.")

import json
import os
from datetime import datetime

LOGS_DIR = "memory/logs"

def log_event(task_id, step_id, agent_role, event, detail=""):
    os.makedirs(LOGS_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "step_id": step_id,
        "agent": agent_role,
        "event": event,       # STARTED / COMPLETED / FAILED / RETRIED / BACKUP_USED / USER_INTERVENED
        "detail": detail
    }
    log_file = f"{LOGS_DIR}/{task_id}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also print to terminal with color coding
    symbols = {
        "STARTED": "→",
        "COMPLETED": "✓",
        "FAILED": "✗",
        "RETRIED": "↻",
        "BACKUP_USED": "⚡",
        "USER_INTERVENED": "⚠"
    }
    symbol = symbols.get(event, "•")
    print(f"  [{entry['timestamp'][11:19]}] {symbol} {agent_role} step {step_id}: {event} {detail}")

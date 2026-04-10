import json
import os
from datetime import datetime
import fcntl

TASKS_DIR = "memory/tasks"
CHECKPOINTS_DIR = "memory/checkpoints"

def create_task(task_id, user_input, plan):
    task = {
        "task_id": task_id,
        "user_input": user_input,
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "plan": plan,
        "steps": {}
    }
    _write(TASKS_DIR, task_id, task)
    return task

def update_step(task_id, step_id, status, output=None):
    task = get_task(task_id)
    task["steps"][step_id] = {
        "status": status,
        "output": output,
        "updated_at": datetime.now().isoformat()
    }
    _write(TASKS_DIR, task_id, task)

def get_task(task_id):
    path = f"{TASKS_DIR}/{task_id}.json"
    with open(path, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def _write(directory, task_id, data):
    os.makedirs(directory, exist_ok=True)
    with open(f"{directory}/{task_id}.json", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def save_checkpoint(task_id, step_id, agent_role, output):
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    checkpoint = {
        "task_id": task_id,
        "step_id": step_id,
        "agent_role": agent_role,
        "output": output,
        "saved_at": datetime.now().isoformat()
    }
    filename = f"{CHECKPOINTS_DIR}/{task_id}_{step_id}.json"
    with open(filename, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(checkpoint, f, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def load_checkpoint(task_id, step_id):
    filename = f"{CHECKPOINTS_DIR}/{task_id}_{step_id}.json"
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def get_last_checkpoint(task_id):
    files = [
        f for f in os.listdir(CHECKPOINTS_DIR)
        if f.startswith(task_id)
    ]
    if not files:
        return None
    files.sort()
    with open(f"{CHECKPOINTS_DIR}/{files[-1]}", "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

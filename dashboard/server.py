from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_loader import load_agents
from core.planner import plan_task
from core.master import run_task
from core.token_tracker import TokenTracker
from core.scope_guard import ScopeGuard
from core.memory import get_task

app = FastAPI(title="NEXUS Dashboard")

# ── Global state ──────────────────────────────────────────────────────
agents = load_agents()
tracker = TokenTracker()
active_tasks = {}   # task_id -> thread status


# ── Request models ────────────────────────────────────────────────────
class TaskRequest(BaseModel):
    user_input: str
    auto_approve: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────
@app.post("/task")
def submit_task(request: TaskRequest):
    """Submit a new task — returns task_id and plan for approval"""
    try:
        task_id, plan = plan_task(agents["planner"], request.user_input)
        
        active_tasks[task_id] = {
            "status": "PENDING_APPROVAL",
            "plan": plan
        }
        
        return {
            "task_id": task_id,
            "plan": plan,
            "total_token_estimate": plan.get("total_token_estimate", 0),
            "status": "PENDING_APPROVAL"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/task/{task_id}/approve")
def approve_task(task_id: str):
    """Approve a planned task and begin execution"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    active_tasks[task_id]["status"] = "RUNNING"
    tracker.init_task(task_id, 
        active_tasks[task_id]["plan"].get("total_token_estimate", 0))

    # Run in background thread so API stays responsive
    thread = threading.Thread(
        target=_execute_task,
        args=(task_id,),
        daemon=True
    )
    thread.start()
    
    return {"task_id": task_id, "status": "RUNNING"}


@app.post("/task/{task_id}/cancel")
def cancel_task(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    active_tasks[task_id]["status"] = "CANCELLED"
    return {"task_id": task_id, "status": "CANCELLED"}


@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    """Get full task state — steps, outputs, token usage"""
    try:
        task = get_task(task_id)
        token_data = tracker.usage.get(task_id, {})
        
        return {
            "task_id": task_id,
            "user_input": task.get("user_input"),
            "status": active_tasks.get(task_id, {}).get("status", "UNKNOWN"),
            "steps": task.get("steps", {}),
            "plan": task.get("plan", {}),
            "tokens": {
                "estimated": token_data.get("estimated", 0),
                "actual": token_data.get("actual", 0),
                "per_step": token_data.get("per_step", {})
            }
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@app.get("/tasks")
def list_tasks():
    """List all known tasks with their statuses"""
    result = []
    tasks_dir = "memory/tasks"
    if os.path.exists(tasks_dir):
        for f in sorted(os.listdir(tasks_dir), reverse=True):
            if f.endswith(".json"):
                task_id = f.replace(".json", "")
                try:
                    task = get_task(task_id)
                    result.append({
                        "task_id": task_id,
                        "user_input": task.get("user_input", "")[:80],
                        "status": active_tasks.get(task_id, {}).get("status", "COMPLETED"),
                        "step_count": len(task.get("steps", {}))
                    })
                except:
                    pass
    return result


@app.get("/agents")
def get_agents():
    """Live agent status — IDLE / WORKING / FAILED"""
    return {
        role: {
            "role": role,
            "model": agent.model,
            "status": agent.status,
            "last_tokens": agent.last_tokens
        }
        for role, agent in agents.items()
        if not role.startswith("mistral")  # hide backup agents from UI
    }


@app.get("/logs/{task_id}")
def get_logs(task_id: str):
    """Return structured log entries for a task"""
    log_file = f"memory/logs/{task_id}.jsonl"
    if not os.path.exists(log_file):
        return []
    entries = []
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries


# ── Static files + HTML ───────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("dashboard/index.html") as f:
        return f.read()


# ── Background execution ──────────────────────────────────────────────
def _execute_task(task_id: str):
    try:
        run_task(task_id, agents, tracker)
        active_tasks[task_id]["status"] = "COMPLETED"
    except SystemExit:
        active_tasks[task_id]["status"] = "CANCELLED"
    except Exception as e:
        active_tasks[task_id]["status"] = "FAILED"
        print(f"Task {task_id} failed: {e}")


if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)

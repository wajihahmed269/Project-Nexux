from datetime import datetime

class TokenTracker:
    def __init__(self, warning_threshold=10000):
        self.threshold = warning_threshold
        self.usage = {}  # task_id -> {estimated, actual, per_step}

    def init_task(self, task_id, estimated_total):
        try:
            estimated_total = int(estimated_total)
        except (ValueError, TypeError):
            estimated_total = 0
            
        self.usage[task_id] = {
            "estimated": estimated_total,
            "actual": 0,
            "per_step": {},
            "started_at": datetime.now().isoformat()
        }
        if estimated_total > self.threshold:
            print(f"\n⚠ WARNING: Estimated tokens ({estimated_total}) exceed threshold ({self.threshold})")
            print("  Consider reducing task scope before proceeding.\n")

    def record_step(self, task_id, step_id, tokens_used):
        if task_id not in self.usage:
            return
        self.usage[task_id]["actual"] += tokens_used
        self.usage[task_id]["per_step"][step_id] = tokens_used

    def summary(self, task_id):
        if task_id not in self.usage:
            return "No data"
        u = self.usage[task_id]
        print(f"\n--- Token Summary ---")
        print(f"  Estimated : {u['estimated']}")
        print(f"  Actual    : {u['actual']}")
        print(f"  Per step  : {u['per_step']}")
        return u

import yaml

def load_settings():
    with open("agents/config.yaml") as f:
        return yaml.safe_load(f).get("settings", {})

class ScopeGuard:
    def __init__(self):
        settings = load_settings()
        self.max_steps = settings.get("max_steps", 10)
        self.max_tokens = settings.get("max_tokens_per_task", 15000)

    def check_steps(self, plan):
        total_steps = sum(
            len(phase["steps"])
            for phase in plan["phases"]
        )
        if total_steps > self.max_steps:
            print(f"\n⚠  Plan has {total_steps} steps — exceeds limit of {self.max_steps}")
            print("  Ask the planner to reduce scope, or increase max_steps in config.yaml")
            choice = input("  Continue anyway? (y/n): ").strip().lower()
            if choice != "y":
                raise SystemExit("Task cancelled — too many steps")

    def check_tokens(self, tracker, task_id):
        usage = tracker.usage.get(task_id, {})
        actual = usage.get("actual", 0)
        if actual >= self.max_tokens:
            print(f"\n⚠  Token limit reached ({actual}/{self.max_tokens})")
            choice = input("  Stop execution? (y/n): ").strip().lower()
            if choice == "y":
                raise SystemExit("Task stopped — token limit reached")

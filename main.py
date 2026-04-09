from core.agent_loader import load_agents
from core.planner import plan_task
from core.master import run_task
from core.token_tracker import TokenTracker

def show_plan(plan):
    print("\n" + "="*50)
    print("NEXUS EXECUTION PLAN")
    print("="*50)
    
    for phase in plan["phases"]:
        print(f"\nPhase {phase['phase']}: {phase['name']}")
        for step in phase["steps"]:
            est = step.get("token_estimate", "?")
            print(f"  [{step['step_id']}] {step['agent'].upper():10} {step['instruction'][:60]}")
            print(f"            ~{est} tokens")
    
    total = plan.get("total_token_estimate", 0)
    print(f"\nTotal estimated tokens: {total}")
    print("="*50)

def get_user_approval(plan):
    show_plan(plan)
    print("\nOptions:")
    print("  [y] Approve and execute")
    print("  [n] Cancel")
    print("  [m] Modify scope (re-plan with a different input)")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == "y":
        return "approved"
    elif choice == "m":
        new_input = input("Enter modified task: ")
        return ("modify", new_input)
    else:
        return "cancelled"

def main():
    agents = load_agents()
    tracker = TokenTracker(warning_threshold=10000)
    
    user_input = input("Enter your task: ")
    
    print("\nPlanning...")
    task_id, plan = plan_task(agents["planner"], user_input)
    
    # Approval loop — user can modify and re-plan
    while True:
        result = get_user_approval(plan)
        
        if result == "approved":
            break
        elif result == "cancelled":
            print("Task cancelled.")
            return
        elif isinstance(result, tuple) and result[0] == "modify":
            print("\nRe-planning with new input...")
            task_id, plan = plan_task(agents["planner"], result[1])
    
    # Initialize token tracking
    tracker.init_task(task_id, plan.get("total_token_estimate", 0))
    
    print(f"\nExecuting task {task_id}...")
    run_task(task_id, agents, tracker)
    
    tracker.summary(task_id)
    print(f"\nAll outputs saved to memory/tasks/{task_id}.json")

if __name__ == "__main__":
    main()

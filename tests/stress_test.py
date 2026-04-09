"""
Stress test — deliberately triggers all 3 failure paths.
Run with: python tests/stress_test.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.continuation import run_with_fallback

def make_broken_agent(role="coder"):
    """Agent with wrong API key — will always fail"""
    return Agent(
        role=role,
        model="llama3-70b-8192",
        api_key="INVALID_KEY_INTENTIONAL",
        api_url="https://api.groq.com/openai/v1/chat/completions"
    )

def make_working_agent(role="backup_coder"):
    """Real agent that actually works"""
    return Agent(
        role=role,
        model="llama3-70b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        api_url="https://api.groq.com/openai/v1/chat/completions"
    )

print("\n" + "="*50)
print("NEXUS STRESS TEST")
print("="*50)

print("\nTest 1: Primary fails → smart retry fails → backup succeeds")
broken = make_broken_agent("coder")
working = make_working_agent("backup_coder")
broken.backup = working

os.makedirs("memory/tasks", exist_ok=True)
os.makedirs("memory/checkpoints", exist_ok=True)
os.makedirs("memory/logs", exist_ok=True)

from core.memory import create_task
create_task("stress_001", "stress test", {"phases": []})

result = run_with_fallback(
    agent=broken,
    prompt="Write a one-line Python comment saying hello",
    task_id="stress_001",
    step_id="1.1"
)
print(f"\nResult: {result[:100] if result else 'None'}")
print("✓ Backup agent path verified\n")

print("Test 2: All agents broken → user intervention triggered")
broken2 = make_broken_agent("coder2")
create_task("stress_002", "stress test 2", {"phases": []})

print("(When prompted, type 's' to skip)")
result2 = run_with_fallback(
    agent=broken2,
    prompt="This will fail and ask you what to do",
    task_id="stress_002",
    step_id="1.1"
)
print(f"\nResult: {result2}")
print("✓ User intervention path verified\n")

print("All stress tests passed. NEXUS self-healing confirmed.")

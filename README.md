# NEXUS — Multi-Agent AI Orchestration System

> A self-healing, model-agnostic AI pipeline that never stops working.

NEXUS treats AI models the way DevOps engineers treat servers — interchangeable
workers managed by a smart controller. If one agent fails, another picks up from
the exact same checkpoint. No restarts. No lost context.

---

## What It Does

- Submit a task in plain English
- Planner breaks it into phases and steps with token estimates
- You approve the plan before anything runs
- Coder → Builder → Reviewer execute automatically
- If any agent fails: smart retry → backup agent → ask you
- Live web dashboard shows every step in real time

---

## Architecture
User Input
↓
Planner Agent        (Gemini — breaks task into steps)
↓
User Approval Gate   (you review plan + token estimate)
↓
Master Controller    (orchestrates execution)
↓
┌─────────────────────────────────────┐
│  Coder → Builder → Reviewer         │
│  (Groq Llama — executes each step)  │
└─────────────────────────────────────┘
↓
Shared Memory        (JSON checkpoints — survives restarts)
↓
Live Dashboard       (FastAPI + HTML — real-time visibility)

---

## Self-Healing Pipeline
Agent fails
→ Smart retry (improved prompt, same agent)
→ Backup agent (different model, same checkpoint)
→ Ask user (skip / retry / cancel)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| HTTP | httpx |
| Memory | JSON files → SQLite (v1.2) |
| Dashboard | FastAPI + vanilla HTML |
| Config | YAML |
| AI Providers | Groq (Llama 3), Google Gemini, Mistral |

**Cost: $0.00** — runs entirely on free API tiers.

---

## Setup (under 30 minutes)

**1. Clone and install**
```bash
git clone https://github.com/wajihahmed269/nexus.git
cd nexus
pip install -r requirements.txt
```

**2. Get free API keys**

| Provider | Get key at |
|----------|-----------|
| Groq | console.groq.com |
| Google Gemini | aistudio.google.com |
| Mistral | console.mistral.ai |

**3. Add keys to .env**
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
MISTRAL_API_KEY=your_key

**4. Start NEXUS**
```bash
# CLI mode
python main.py

# Dashboard mode
python dashboard/server.py
# Open http://localhost:8000
```

---

## Demo Tasks

### Task 1 — Code generation
**Input:** "Write a Python class for a task queue with push, pop, and size methods"

**What happened:**
- Planner broke it into 3 steps across 2 phases
- Coder generated the class (Groq Llama 3)
- Reviewer caught a missing edge case on empty pop
- Final output: corrected, documented class

### Task 2 — Multi-step pipeline
**Input:** "Write a Python function that reads a CSV and returns summary statistics"

**What happened:**
- 4 steps across 3 phases
- Builder assembled imports + function into one clean file
- All 4 agents ran in sequence
- Total tokens used: ~1,200

### Task 3 — Self-healing in action
**Input:** "Write a Dockerfile for a Python FastAPI app"

**What happened:**
- Primary coder agent hit rate limit
- Smart retry fired automatically with improved prompt
- Retry succeeded — backup agent never needed
- User saw the retry in the live dashboard log

---

## DevOps Parallels

| NEXUS Component | DevOps Equivalent |
|-----------------|-------------------|
| Master Controller | Kubernetes Scheduler |
| Smart retry + continuation | Health checks + restart policy |
| Shared memory + checkpoints | Persistent volumes |
| config.yaml | Helm values file |
| Multi-model failover | Multi-AZ deployment |
| Live dashboard | Grafana + Prometheus |
| Failure logs | Structured log aggregation |
| Token tracking | Resource monitoring |

---

## Project Structure
nexus/
├── core/
│   ├── agent.py           # Agent class — wraps any model API
│   ├── agent_loader.py    # Loads agents from config.yaml
│   ├── master.py          # Orchestration logic
│   ├── memory.py          # Shared state — tasks + checkpoints
│   ├── planner.py         # Task breakdown + token estimation
│   ├── continuation.py    # Smart retry + backup + user prompt
│   ├── token_tracker.py   # Estimated vs actual usage
│   ├── scope_guard.py     # Step + token limits
│   └── logger.py          # Structured JSONL event logs
├── agents/
│   └── config.yaml        # All agent definitions
├── prompts/               # System prompts per agent role
├── memory/
│   ├── tasks/             # One JSON per task
│   ├── checkpoints/       # Auto-saved after each step
│   └── logs/              # JSONL failure + event logs
├── dashboard/
│   ├── server.py          # FastAPI — 7 endpoints
│   └── index.html         # Live dashboard UI
├── tests/
│   ├── test_agent.py
│   ├── test_memory.py
│   └── test_continuation.py
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── CHANGELOG.md

---

## Roadmap

| Version | Feature |
|---------|---------|
| v1.2 | Vector memory — ChromaDB replaces JSON |
| v1.3 | Parallel agent execution |
| v1.4 | Custom roles defined from dashboard |
| v1.5 | Pre-built DevOps pipelines |
| v2.0 | SaaS packaging — Docker + login system |

---

## Author

**Wajih Ahmed** — DevOps Engineer in training  
[GitHub](https://github.com/wajihahmed269) · 
[LinkedIn](https://linkedin.com/in/wajih-ahmed-041235391)

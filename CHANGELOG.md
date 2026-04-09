# NEXUS Changelog

All decisions and improvements are documented here. Nothing is deleted.

---

## v1.0 — March 2025 — Original Blueprint

**Status: COMPLETE**

- Designed 5-component architecture: Master Controller, Agent Pool,
  Shared Memory, Continuation Engine, Dashboard
- 21-day build plan across 3 phases
- Starter code: agent.py, memory.py, continuation.py, config.yaml
- DevOps mapping table established
- Free API strategy: Groq + Gemini + Mistral

---

## v1.1 — March 2025 — Blueprint Refinement

**Status: COMPLETE**

- Added document-first execution: plan shown before any agent runs
- Added token awareness: estimate displayed before execution starts
- Upgraded continuation engine: smart retry before backup agent
- Added user intervention step if all fallbacks fail
- Intentional scope limits in v1: no parallel execution
- Added CHANGELOG.md and token_tracker.py to folder structure
- Updated config.yaml with mode, retry_limit, token_warning

---

## v1.2 — April 2025 — Full Build

**Status: CURRENT**

**Phase 1 — Foundation**
- Built Agent class with status tracking (IDLE/WORKING/FAILED)
- Multi-model support: same class works with Groq and Gemini
- memory.py: create_task(), update_step(), get_task()
- planner.py: structured JSON plan with token estimates
- master.py: orchestration loop with context passing

**Phase 2 — Core Pipeline**
- token_tracker.py: estimated vs actual per step
- User-approval flow: plan shown before execution, modify/cancel supported
- System prompts loaded from prompts/ directory
- Checkpoint system: auto-saved after every step
- Structured JSONL logging: every event timestamped

**Phase 3 — Intelligence**
- 3 failure types: TIMEOUT, EMPTY_RESPONSE, API_ERROR
- Smart retry: improved prompt with error context
- Backup agent handoff from checkpoint
- User intervention: skip / retry / cancel
- Scope limits: max_steps, max_tokens_per_task
- Full test suite: test_agent, test_memory, test_continuation

**Phase 4 — Dashboard**
- FastAPI server with 7 endpoints
- Live dashboard: agent badges, step progress, token bar, event log
- Approval modal: review plan in browser before execution
- Background threading: dashboard stays responsive during execution
- EC2 deployable

**Phase 5 — Ship**
- Docker + docker-compose
- README with setup guide and demo tasks
- GitHub public repo
- LinkedIn post series

---

## v1.3 — PLANNED

- Replace JSON memory with ChromaDB vector store
- Agents can search past task history
- Parallel execution for independent steps

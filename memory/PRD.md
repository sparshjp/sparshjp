# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: No login required. Creator Mode (password-gated) for Kairos AI Engine access
- **AI**: Kairos AI Engine v4 + Prompt Compressor + 6 LLM providers + 33 tools + 4 subagents
- **Events**: `module_events.py` — cross-module triggers

## What's Been Implemented

### Phase 1-8 — Core ERP through Free LLM Providers (Done)
### Phase 9 — Kairos Subagent Upgrade to E1 Parity (Done)

### Phase 10 — Smart Prompt Compression Agent (Done — April 9, 2026)
- **`prompt_compressor.py`** — Algorithmic 5-stage compression pipeline with protected content preservation:
  1. Protected Content Extraction (TOOL_CALL format, tool names, code patterns)
  2. Section Priority Ranking (identity > tools > modules > rules > examples)
  3. Redundancy Elimination (dedup lines)
  4. Markdown/Syntax Stripping
  5. Abbreviation Engine + Example Pruning
- **Results**: 32% compression for Groq (10919→3491 chars), 42% for Cerebras/HuggingFace
- **Benchmark**: 18 tests validating quality — all critical patterns preserved
- **Caching**: Compressed prompts cached by hash — no re-computation
- **Stats endpoint**: GET /api/agents/compression-stats

### Phase 11 — Tool Registry Refactor (Done — April 9, 2026)
- Extracted 750+ line `execute_tool` monolith from `routes_agents.py` into `kairos_tools.py`
- `TOOL_REGISTRY` dict maps 33 tool names → async handler functions
- `execute_tool` in `routes_agents.py` reduced to 6-line dispatcher
- `routes_agents.py`: 2449 → 1292 lines (47% reduction)
- Dependencies injected via `configure(db, is_safe_path, audit_fn)`
- Compound tools (`scaffold_module`, `create_page`) + helpers (`_polish_generated_python`, `_auto_fix_startup_error`, `_run_test_query`) also moved
- **Tested**: 32/32 tests passed (iteration_39)

## LLM Provider Priority
1. FREE (compressed): Groq → Cerebras → HuggingFace
2. Direct Keys (full prompt): Anthropic → OpenAI → OpenRouter
3. Emergent Credits (full prompt): Claude → Gemini → GPT-5

## Key Files
- `/app/backend/kairos_tools.py` — 33 tool handlers + TOOL_REGISTRY
- `/app/backend/routes_agents.py` — AI Engine routes + LLM client + agentic loop
- `/app/backend/prompt_compressor.py` — Smart compression pipeline
- `/app/backend/kairos_subagents.py` — v2 subagents
- `/app/backend/tests/compression_benchmark.py` — 18 quality tests

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness

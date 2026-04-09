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
- **`prompt_compressor.py`** — Algorithmic 5-stage compression pipeline:
  1. Section Priority Ranking (identity > tools > modules > rules > examples)
  2. Redundancy Elimination (dedup lines)
  3. Markdown/Syntax Stripping
  4. Abbreviation Engine (verbose → concise patterns)
  5. Example Pruning (keep structure, remove verbose content)
- **Results**: 68% compression for Groq (10919→3481 chars), 64% for Cerebras/HuggingFace
- **Caching**: Compressed prompts cached by hash — no re-computation
- **Stats endpoint**: GET /api/agents/compression-stats
- **Verified**: Kairos uses tools correctly (read_file, run_test, etc.) with compressed prompts on Groq free tier

## LLM Provider Priority
1. FREE (compressed): Groq → Cerebras → HuggingFace
2. Direct Keys (full prompt): Anthropic → OpenAI → OpenRouter
3. Emergent Credits (full prompt): Claude → Gemini → GPT-5

## Key Files
- `/app/backend/prompt_compressor.py` — Smart compression pipeline
- `/app/backend/kairos_subagents.py` — v2 subagents
- `/app/backend/routes_agents.py` — 33-tool Kairos Engine

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness
- P3: Refactor routes_agents.py

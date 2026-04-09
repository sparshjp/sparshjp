# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: No login required. Creator Mode (password-gated) for Kairos AI Engine access
- **AI**: Kairos AI Engine v4 + Prompt Compressor + 6 LLM providers + 35 tools + 4 subagents
- **Events**: `module_events.py` — cross-module triggers
- **Kairos Independence**: Kairos loads FIRST in server.py, ERP modules isolated via `_safe_load()`

## What's Been Implemented

### Phase 1-9 — Core ERP through Subagent Upgrade (Done)
### Phase 10 — Smart Prompt Compression (Done — April 9, 2026)
### Phase 11 — Tool Registry Refactor (Done — April 9, 2026)

### Phase 12 — Knowledge Repository + Kairos Independence (Done — April 9, 2026)
- **Knowledge Base** (`/app/backend/kairos_knowledge.md`): 13 sections covering architecture, file map, all 35 tools, compression pipeline, LLM providers, DB collections, common patterns, debugging recipes, security boundaries, subagents, self-repair checklist, and how to add new tools
- **2 New Tools**: `read_knowledge(section?)` reads knowledge base, `update_knowledge(entry)` appends learnings
- **Kairos Independence**: Restructured `server.py` so Kairos registers BEFORE all ERP modules in its own try/except. Each of the 37 ERP modules loads via `_safe_load()` — individual isolation so one failing module doesn't crash others or Kairos
- **`audit_trail` decoupled**: Imported at module level with a no-op fallback stub, preventing NameError cascades
- **System Status**: `GET /api/system/status` reports `kairos: online/offline`, loaded/failed module counts
- **Tested**: 39/39 tests passed (iteration_40)

## Key Architecture Decision: Kairos → ERP (one-way dependency)
Kairos CAN modify/query ERP collections and files.
ERP CANNOT affect Kairos availability — they're isolated at startup.
If an ERP module crashes, Kairos remains online and can diagnose/fix it.

## LLM Provider Priority
1. FREE (compressed): Groq → Cerebras → HuggingFace
2. Direct Keys (full prompt): Anthropic → OpenAI → OpenRouter
3. Emergent Credits (full prompt): Claude → Gemini → GPT-5

## Key Files
- `/app/backend/kairos_knowledge.md` — Knowledge repository (35 tools, 13 sections)
- `/app/backend/kairos_tools.py` — 35 tool handlers + TOOL_REGISTRY
- `/app/backend/routes_agents.py` — AI Engine routes + LLM client + agentic loop
- `/app/backend/prompt_compressor.py` — Smart compression pipeline
- `/app/backend/kairos_subagents.py` — v2 subagents
- `/app/backend/server.py` — Kairos-first registration + isolated ERP loading

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness

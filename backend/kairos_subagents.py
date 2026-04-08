"""Kairos Subagents — Specialized AI agents for testing, design, integration, and troubleshooting."""
import uuid
import os
import json
import logging

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


def _get_key():
    """Get the LLM key at call time (not import time) so .env changes are picked up."""
    return os.environ.get("EMERGENT_LLM_KEY", "") or EMERGENT_KEY

# ═══════════════════════════════════════════
# SUBAGENT SYSTEM PROMPTS
# ═══════════════════════════════════════════

TESTER_PROMPT = """You are a **Testing Expert Subagent** for the Kairos AI Engine inside ABC Ltd IT ERP.
Your job: Given a feature description and file paths, generate a comprehensive test plan and test commands.

Output format:
1. **Test Plan** — List of test cases (endpoint, expected behavior, method)
2. **Backend Tests** — curl commands or Python test scripts that can be run directly
3. **Frontend Tests** — Key UI elements and routes to verify
4. **Edge Cases** — Boundary conditions, error scenarios

Tech: FastAPI backend (port 8001, prefix /api), React frontend (port 3000), MongoDB.
Always use http://localhost:8001 for API tests.
Be specific — provide exact curl commands with example payloads."""

DESIGNER_PROMPT = """You are a **UI/UX Design Expert Subagent** for the Kairos AI Engine inside ABC Ltd IT ERP.
Given a page/feature description, output a complete design specification.

Design system:
- Dark theme: bg #0D1B2A, cards #152236, borders #1B2D42, text #E8EDF2, accent #00d4aa
- Font: System sans-serif stack
- Icons: Lucide React
- Components: Shadcn/UI (from ../components/ui/*)
- Spacing: Tailwind CSS classes
- Responsive: Mobile-first

Output format:
1. **Component Hierarchy** — React component tree
2. **Layout** — Tailwind grid/flex structure with exact classes
3. **States** — Loading, empty, error, populated
4. **Interactions** — Hover, click, transitions
5. **Code Skeleton** — JSX template with Tailwind classes (ready to copy)

Do NOT use emoji icons. Use Lucide React icons only."""

INTEGRATOR_PROMPT = """You are an **Integration Expert Subagent** for the Kairos AI Engine inside ABC Ltd IT ERP.
Given a third-party service/API, provide a complete integration playbook.

Output format:
1. **Requirements** — API keys, packages, env vars needed
2. **Installation** — pip/yarn install commands
3. **Backend Code** — FastAPI route with full implementation
4. **Frontend Code** — React component with API calls
5. **Environment** — .env entries needed
6. **Testing** — How to verify the integration works
7. **Common Issues** — Known gotchas and fixes

Tech: FastAPI + Motor (MongoDB) backend, React + Tailwind frontend.
Always use async/await for backend. Use httpx for external API calls."""

TROUBLESHOOTER_PROMPT = """You are a **Troubleshooting Expert Subagent** for the Kairos AI Engine inside ABC Ltd IT ERP.
Given an error description, logs, and context, perform root cause analysis.

Output format:
1. **Diagnosis** — What is likely causing the issue (ranked by probability)
2. **Root Cause** — The specific code/config/data problem
3. **Fix Steps** — Exact code changes or commands to resolve
4. **Verification** — How to confirm the fix works
5. **Prevention** — How to prevent recurrence

Tech: FastAPI + Motor (MongoDB), React + Tailwind, MongoDB.
Backend logs: /var/log/supervisor/backend.*.log
Frontend logs: /var/log/supervisor/frontend.*.log
Be specific — provide exact file paths, line numbers, and code changes."""


async def call_subagent(agent_type: str, task: str, context: str = "") -> dict:
    """Call a specialized subagent with a focused task."""
    prompts = {
        "tester": TESTER_PROMPT,
        "designer": DESIGNER_PROMPT,
        "integrator": INTEGRATOR_PROMPT,
        "troubleshooter": TROUBLESHOOTER_PROMPT,
    }

    system = prompts.get(agent_type)
    if not system:
        return {"status": "error", "error": f"Unknown agent_type: {agent_type}. Use: tester, designer, integrator, troubleshooter"}

    key = _get_key()
    if not key:
        return {"status": "error", "error": "No LLM key configured"}

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=key,
            session_id=f"subagent-{agent_type}-{uuid.uuid4()}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        full_task = task
        if context:
            full_task = f"CONTEXT:\n{context}\n\nTASK:\n{task}"

        response = await chat.send_message(UserMessage(text=full_task))
        if not response:
            return {"status": "error", "error": "Subagent returned empty response"}

        return {
            "status": "ok",
            "agent_type": agent_type,
            "response": response[:12000],
            "full_length": len(response),
        }
    except Exception as e:
        return {"status": "error", "error": f"Subagent call failed: {str(e)}"}


async def generate_image(prompt: str, size: str = "1024x1024") -> dict:
    """Generate an image using OpenAI GPT Image 1 via Emergent."""
    key = _get_key()
    if not key:
        return {"status": "error", "error": "No LLM key configured"}

    try:
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        import base64 as b64

        image_gen = OpenAIImageGeneration(api_key=key)
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=1,
        )

        if images and len(images) > 0:
            # Save to file and return path
            img_id = str(uuid.uuid4())[:8]
            img_path = f"/app/backend/uploads/generated_{img_id}.png"
            os.makedirs("/app/backend/uploads", exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(images[0])

            # Also create base64 for inline display
            image_base64 = b64.b64encode(images[0]).decode('utf-8')
            file_size = len(images[0])

            return {
                "status": "ok",
                "prompt": prompt,
                "path": img_path,
                "image_url": f"data:image/png;base64,{image_base64[:100]}...",  # Truncated for response
                "file_size_kb": round(file_size / 1024, 1),
                "serve_url": f"/api/agents/screenshots/generated_{img_id}.png",
            }
        else:
            return {"status": "error", "error": "No image was generated"}
    except Exception as e:
        return {"status": "error", "error": f"Image generation failed: {str(e)}"}

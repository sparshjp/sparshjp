"""Kairos Subagents v2 — Enterprise-grade AI agents matching E1 capabilities.

Includes:
- Testing Agent v3: Browser automation (Playwright) + API testing + test reports
- Design Agent: Full UI/UX design system generation
- Integration Playbook Expert: Verified playbooks for 30+ services
- Troubleshoot Agent: Structured 10-step RCA methodology
"""
import uuid
import os
import json
import logging
import asyncio
import subprocess
import traceback
from datetime import datetime, timezone

logger = logging.getLogger("kairos.subagents")
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000")


def _get_key():
    return os.environ.get("EMERGENT_LLM_KEY", "") or EMERGENT_KEY


# ═══════════════════════════════════════════════════════════
# TESTING AGENT v3 — Browser Automation + API + Reports
# ═══════════════════════════════════════════════════════════

TESTER_V3_PROMPT = """You are the **Kairos Testing Agent v3** — an enterprise-grade testing engine for ABC Ltd IT ERP.
You generate comprehensive test suites that cover backend API, frontend UI (Playwright browser automation), and integration tests.

## Your Capabilities
1. **Backend API Tests** — Generate curl commands and Python requests scripts for every endpoint
2. **Frontend Browser Tests** — Generate Playwright Python scripts that automate the browser: navigate, click, fill forms, take screenshots, assert text
3. **Integration Tests** — Test cross-module workflows (e.g., Contract → Project → Billing chain)
4. **Test Reports** — Output structured JSON reports with pass/fail/skip for each test case

## Tech Stack
- Backend: FastAPI on http://localhost:8001, all routes prefixed with /api
- Frontend: React on port 3000, Shadcn UI, dark theme (#0D1B2A)
- Database: MongoDB (Motor async driver)
- Auth: JWT token from POST /api/auth/login with email/password
- Login credentials: email=kairoserp, password=¢re@tor@AIengine

## Output Format
Return a JSON object:
```json
{
  "test_plan": [
    {"id": "T1", "category": "backend|frontend|integration", "name": "...", "priority": "high|medium|low"}
  ],
  "backend_tests": [
    {
      "id": "T1",
      "name": "...",
      "type": "curl|python",
      "command": "curl -X POST http://localhost:8001/api/... -H 'Content-Type: application/json' -d '{...}'",
      "expected": "status 200, response contains ...",
      "validate": "response.status_code == 200 and 'key' in response.json()"
    }
  ],
  "frontend_tests": [
    {
      "id": "T5",
      "name": "...",
      "playwright_script": "async def test(page):\\n    await page.goto('http://localhost:3000')\\n    ...",
      "expected": "Page shows ..., button is clickable",
      "screenshot": true
    }
  ],
  "integration_tests": [
    {
      "id": "T8",
      "name": "Cross-module: Contract creates Project",
      "steps": ["Create contract via API", "Verify project auto-created", "Check billing entry"],
      "script": "..."
    }
  ]
}
```

## Rules
- ALWAYS include data-testid selectors for frontend tests (the app uses them extensively)
- ALWAYS test both happy path AND error cases
- ALWAYS verify database state after write operations
- For frontend: use page.wait_for_timeout(1000) between actions, use force=True for clicks
- Generate EXECUTABLE scripts — no pseudo-code
- Test auth flows first, then module-specific flows
- Screenshots at key steps: await page.screenshot(path='/tmp/test_X.png')"""


TESTER_V3_RUNNER_PROMPT = """You are the Kairos Test Runner. Given test scripts, execute them and produce a structured test report.
Format your response as JSON:
```json
{
  "total": N,
  "passed": N,
  "failed": N,
  "skipped": N,
  "duration_seconds": N,
  "tests": [
    {"id": "T1", "name": "...", "status": "pass|fail|skip", "duration": "1.2s", "error": null, "screenshot": null}
  ],
  "summary": "..."
}
```"""


async def run_playwright_test(script: str, test_name: str = "test") -> dict:
    """Execute a Playwright test script and return results."""
    test_file = f"/tmp/kairos_test_{uuid.uuid4().hex[:8]}.py"
    wrapper = f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({{"width": 1920, "height": 800}})
        results = []
        try:
{_indent(script, 12)}
            results.append({{"status": "pass", "message": "Test completed"}})
        except Exception as e:
            results.append({{"status": "fail", "error": str(e)}})
            await page.screenshot(path='/tmp/kairos_test_fail.png')
        finally:
            await browser.close()
        return results

import json
r = asyncio.run(main())
print(json.dumps(r))
"""
    try:
        with open(test_file, 'w') as f:
            f.write(wrapper)

        proc = await asyncio.create_subprocess_exec(
            'python3', test_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        output = stdout.decode().strip()

        try:
            results = json.loads(output)
            return {"status": "ok", "test_name": test_name, "results": results}
        except json.JSONDecodeError:
            return {"status": "ok", "test_name": test_name, "raw_output": output, "stderr": stderr.decode()[:500]}
    except asyncio.TimeoutError:
        return {"status": "error", "test_name": test_name, "error": "Test timed out (60s)"}
    except Exception as e:
        return {"status": "error", "test_name": test_name, "error": str(e)}
    finally:
        try:
            os.remove(test_file)
        except OSError:
            pass


async def run_api_test(command: str, test_name: str = "api_test") -> dict:
    """Execute a curl or Python API test command."""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode().strip()
        return {
            "status": "pass" if proc.returncode == 0 else "fail",
            "test_name": test_name,
            "output": output[:2000],
            "returncode": proc.returncode,
        }
    except asyncio.TimeoutError:
        return {"status": "fail", "test_name": test_name, "error": "Command timed out (30s)"}
    except Exception as e:
        return {"status": "fail", "test_name": test_name, "error": str(e)}


async def run_test_suite(tests: list) -> dict:
    """Execute a batch of tests and produce a structured report."""
    report = {"total": len(tests), "passed": 0, "failed": 0, "skipped": 0, "tests": [], "timestamp": datetime.now(timezone.utc).isoformat()}

    for test in tests:
        test_type = test.get("type", "curl")
        test_id = test.get("id", "?")
        test_name = test.get("name", "unnamed")

        if test_type == "playwright":
            result = await run_playwright_test(test.get("script", "pass"), test_name)
        elif test_type in ("curl", "python", "bash"):
            result = await run_api_test(test.get("command", "echo 'no command'"), test_name)
        else:
            result = {"status": "skip", "test_name": test_name, "error": f"Unknown type: {test_type}"}

        status = "pass" if result.get("status") == "pass" or result.get("status") == "ok" else "fail"
        if result.get("results"):
            for r in result["results"]:
                if r.get("status") == "fail":
                    status = "fail"
                    break

        report["tests"].append({"id": test_id, "name": test_name, "status": status, "details": result})
        if status == "pass":
            report["passed"] += 1
        else:
            report["failed"] += 1

    # Save report
    report_dir = "/app/test_reports"
    os.makedirs(report_dir, exist_ok=True)
    existing = [f for f in os.listdir(report_dir) if f.startswith("kairos_")]
    report_num = len(existing) + 1
    report_path = f"{report_dir}/kairos_test_{report_num}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    report["report_path"] = report_path
    return report


# ═══════════════════════════════════════════════════════════
# DESIGN AGENT — Full UI/UX Design System Generation
# ═══════════════════════════════════════════════════════════

DESIGNER_V2_PROMPT = """You are the **Kairos Design Agent** — a top-tier UI/UX design expert for ABC Ltd IT ERP.
You create comprehensive, production-ready design specifications that match or exceed professional design systems.

## Your Design Philosophy
- **Avoid AI slop**: No purple gradients on white, no generic card grids, no overused Inter font
- **Commit to a cohesive aesthetic**: Use CSS variables, dominant colors with sharp accents
- **Dark theme mastery**: Solid dark backgrounds (never gradient), depth via z-index, glass-morphism (12-24px backdrop blur)
- **Asymmetric layouts**: Left-aligned, 2-3x more spacing than feels comfortable
- **Micro-animations**: Every interaction has hover states, transitions, entrance animations
- **Modern buttons**: Pill-shaped or sharp-edged with interaction animations

## ERP Design System
- Background: #060e1a (page), #0D1B2A (sidebar/cards), #152236 (elevated), #1B2D42 (borders)
- Text: #E8EDF2 (primary), #7A8BA0 (secondary), #4A5B6E (muted)
- Accents: #00C9A7 (primary action), #a78bfa (creator/special), #ef4444 (danger), #f97316 (warning)
- Components: Shadcn/UI from /app/frontend/src/components/ui/
- Icons: Lucide React ONLY (no emoji)
- Font: System sans-serif stack
- Responsive: Mobile-first with sm:/md:/lg: breakpoints

## Text Size Hierarchy
- H1: text-4xl sm:text-5xl lg:text-6xl
- H2: text-base md:text-lg
- Body: text-base (mobile: text-sm)
- Small/Accent: text-sm or text-xs

## Output Format
Your response MUST be a complete, copy-paste-ready design specification:

```json
{
  "design_system": {
    "color_palette": {"primary": "#00C9A7", ...},
    "typography": {...},
    "spacing": {...},
    "shadows": {...}
  },
  "component_hierarchy": {
    "PageWrapper": {"children": ["Header", "ContentGrid", "ActionBar"]},
    ...
  },
  "layout_spec": {
    "grid": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
    "sections": [...]
  },
  "states": {
    "loading": "Skeleton shimmer with bg-[#152236] animate-pulse",
    "empty": "Centered illustration + CTA button",
    "error": "Red border card with retry button",
    "populated": "Data grid with hover highlights"
  },
  "interactions": {
    "hover": "scale-[1.02] transition-transform duration-200",
    "click": "scale-[0.98] active:bg-opacity-80",
    "entrance": "animate-in fade-in slide-in-from-bottom-4 duration-300"
  },
  "jsx_skeleton": "... complete JSX with Tailwind classes ..."
}
```

Create distinctive, surprising designs. Every page should feel crafted, not generated."""


# ═══════════════════════════════════════════════════════════
# INTEGRATION PLAYBOOK EXPERT — Verified Playbooks
# ═══════════════════════════════════════════════════════════

# Pre-verified integration playbooks for common services
VERIFIED_PLAYBOOKS = {
    "stripe": {
        "name": "Stripe Payments",
        "packages": {"backend": ["stripe>=8.0.0"], "frontend": ["@stripe/stripe-js", "@stripe/react-stripe-js"]},
        "env_vars": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET"],
        "backend_pattern": """
from fastapi import APIRouter, HTTPException, Request
import stripe, os

router = APIRouter(prefix="/payments")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@router.post("/create-checkout")
async def create_checkout(body: dict):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": body.get("currency","usd"), "product_data": {"name": body["product_name"]}, "unit_amount": int(body["amount"] * 100)}, "quantity": 1}],
        mode="payment",
        success_url=body.get("success_url", "http://localhost:3000/success"),
        cancel_url=body.get("cancel_url", "http://localhost:3000/cancel"),
    )
    return {"session_id": session.id, "url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    event = stripe.Webhook.construct_event(payload, sig, os.environ.get("STRIPE_WEBHOOK_SECRET"))
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Handle successful payment
    return {"status": "ok"}
""",
        "testing": "curl -X POST http://localhost:8001/api/payments/create-checkout -H 'Content-Type: application/json' -d '{\"product_name\":\"Test\",\"amount\":10}'",
        "common_issues": ["Webhook signature verification fails in dev — use stripe listen --forward-to", "Amount must be in cents (multiply by 100)"],
    },
    "openai": {
        "name": "OpenAI GPT / Image Generation",
        "packages": {"backend": ["openai>=1.30.0"]},
        "env_vars": ["OPENAI_API_KEY"],
        "backend_pattern": """
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def chat_completion(messages, model="gpt-4o"):
    response = await client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content

async def generate_image(prompt, size="1024x1024"):
    response = await client.images.generate(model="dall-e-3", prompt=prompt, size=size, n=1)
    return response.data[0].url
""",
    },
    "sendgrid": {
        "name": "SendGrid Email",
        "packages": {"backend": ["sendgrid>=6.10.0"]},
        "env_vars": ["SENDGRID_API_KEY", "SENDGRID_FROM_EMAIL"],
        "backend_pattern": """
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

async def send_email(to_email, subject, html_content):
    message = Mail(from_email=os.environ.get("SENDGRID_FROM_EMAIL"), to_emails=to_email, subject=subject, html_content=html_content)
    sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    response = sg.send(message)
    return {"status_code": response.status_code}
""",
    },
    "razorpay": {
        "name": "Razorpay Payments (India)",
        "packages": {"backend": ["razorpay>=1.4.0"]},
        "env_vars": ["RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET"],
        "backend_pattern": """
import razorpay, os

client = razorpay.Client(auth=(os.environ.get("RAZORPAY_KEY_ID"), os.environ.get("RAZORPAY_KEY_SECRET")))

async def create_order(amount_inr, currency="INR"):
    order = client.order.create({"amount": int(amount_inr * 100), "currency": currency, "payment_capture": 1})
    return {"order_id": order["id"], "amount": order["amount"]}
""",
    },
    "twilio": {
        "name": "Twilio SMS",
        "packages": {"backend": ["twilio>=9.0.0"]},
        "env_vars": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"],
    },
    "firebase_auth": {
        "name": "Firebase Authentication",
        "packages": {"backend": ["firebase-admin>=6.0.0"], "frontend": ["firebase"]},
        "env_vars": ["FIREBASE_SERVICE_ACCOUNT_JSON"],
    },
    "aws_s3": {
        "name": "AWS S3 File Storage",
        "packages": {"backend": ["boto3>=1.34.0"]},
        "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_BUCKET", "AWS_REGION"],
    },
    "redis": {
        "name": "Redis Cache",
        "packages": {"backend": ["redis>=5.0.0"]},
        "env_vars": ["REDIS_URL"],
    },
    "elasticsearch": {
        "name": "Elasticsearch",
        "packages": {"backend": ["elasticsearch>=8.0.0"]},
        "env_vars": ["ELASTICSEARCH_URL"],
    },
    "groq": {
        "name": "Groq LLM (Free Tier)",
        "packages": {"backend": ["groq>=0.9.0"]},
        "env_vars": ["GROQ_API_KEY"],
        "backend_pattern": """
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat(messages, model="llama-3.3-70b-versatile"):
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=8000)
    return response.choices[0].message.content
""",
        "common_issues": ["Free tier: 30 requests/min, 1M tokens/day", "Use llama-3.3-70b-versatile for best quality"],
    },
    "cerebras": {
        "name": "Cerebras LLM (Free Tier)",
        "packages": {"backend": ["cerebras-cloud-sdk>=1.0.0"]},
        "env_vars": ["CEREBRAS_API_KEY"],
        "backend_pattern": """
from cerebras.cloud.sdk import Cerebras
import os

client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

def chat(messages, model="llama-3.3-70b"):
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=8000)
    return response.choices[0].message.content
""",
        "common_issues": ["Free tier: 1M tokens/day, ~2000 tokens/sec", "Supports Llama 3.3 70B"],
    },
    "huggingface": {
        "name": "HuggingFace Inference (Free Tier)",
        "packages": {"backend": ["huggingface_hub>=0.25.0"]},
        "env_vars": ["HUGGINGFACE_API_KEY"],
        "backend_pattern": """
from huggingface_hub import InferenceClient
import os

client = InferenceClient(api_key=os.environ.get("HUGGINGFACE_API_KEY"))

def chat(messages, model="Qwen/Qwen2.5-Coder-32B-Instruct"):
    response = client.chat_completion(model=model, messages=messages, max_tokens=8000)
    return response.choices[0].message.content
""",
        "common_issues": ["Free tier has rate limits", "Best coding model: Qwen2.5-Coder-32B-Instruct"],
    },
}

INTEGRATOR_V2_PROMPT = f"""You are the **Kairos Integration Playbook Expert** — providing verified, production-tested integration playbooks.

## Verified Playbooks Available
You have pre-verified playbooks for: {', '.join(VERIFIED_PLAYBOOKS.keys())}

When a user asks for an integration that matches a verified playbook, use it directly.
When there's no verified playbook, generate one from your knowledge following the same format.

## Output Format
```json
{{
  "service": "service_name",
  "verified": true|false,
  "packages": {{"backend": ["pkg>=version"], "frontend": ["pkg"]}},
  "env_vars_needed": ["KEY_NAME — description — where to get it"],
  "installation": "pip install ... && cd /app/frontend && yarn add ...",
  "backend_code": {{
    "file": "/app/backend/routes_integration.py",
    "code": "... complete code ..."
  }},
  "frontend_code": {{
    "file": "/app/frontend/src/components/Integration.js",
    "code": "... complete code ..."
  }},
  "server_registration": "Code to add to server.py to register the router",
  "env_entries": "Lines to add to backend/.env",
  "testing": {{
    "curl_commands": ["curl ..."],
    "expected_responses": ["{{...}}"]
  }},
  "common_issues": ["Issue 1 — fix", "Issue 2 — fix"],
  "security_notes": ["Never expose keys to frontend", "Validate webhooks"]
}}
```

## Rules
- ALWAYS use async/await for backend Python code
- ALWAYS use environment variables for secrets (never hardcode)
- ALWAYS include error handling and proper HTTP status codes
- ALWAYS include testing commands
- For FastAPI: use APIRouter with set_db pattern matching the existing codebase
- For React: use fetch with API from '../App', Shadcn UI components, Tailwind classes
"""


# ═══════════════════════════════════════════════════════════
# TROUBLESHOOT AGENT — Structured 10-Step RCA
# ═══════════════════════════════════════════════════════════

TROUBLESHOOTER_V2_PROMPT = """You are the **Kairos Troubleshoot Agent** — performing systematic root cause analysis (RCA) in 10 steps or fewer.

## Methodology: Structured RCA
Follow this exact investigation framework:

### Phase 1: Gather Evidence (Steps 1-3)
1. **Read error messages** — Extract exact error text, stack traces, HTTP codes
2. **Check logs** — Backend: /var/log/supervisor/backend.*.log, Frontend: browser console
3. **Identify timeline** — When did it start? What changed? Check git log.

### Phase 2: Isolate (Steps 4-6)
4. **Reproduce** — Exact steps/curl commands to trigger the error
5. **Narrow scope** — Is it backend, frontend, database, or network?
6. **Check dependencies** — MongoDB connection, API keys, env vars, disk space

### Phase 3: Root Cause (Steps 7-8)
7. **Trace the code path** — Follow the request from frontend → API route → handler → DB
8. **Identify the exact failure point** — File, line number, variable state

### Phase 4: Fix & Verify (Steps 9-10)
9. **Propose fix** — Exact code change with file path and line numbers
10. **Verify** — Commands to confirm the fix works + regression check

## Output Format
```json
{
  "severity": "critical|high|medium|low",
  "category": "backend_crash|frontend_error|db_connection|auth_failure|integration_error|config_issue",
  "investigation_steps": [
    {"step": 1, "action": "Read error logs", "finding": "...", "command": "tail -50 /var/log/..."},
    ...
  ],
  "root_cause": {
    "file": "/app/backend/server.py",
    "line": 42,
    "description": "...",
    "evidence": "..."
  },
  "fix": {
    "changes": [
      {"file": "...", "old_code": "...", "new_code": "...", "explanation": "..."}
    ],
    "commands": ["pip install ...", "sudo supervisorctl restart backend"]
  },
  "verification": {
    "commands": ["curl ...", "python3 -c '...'"],
    "expected": "200 OK, no errors in logs"
  },
  "prevention": "Add input validation / error handling / monitoring for ..."
}
```

## Tech Context
- Backend: FastAPI + Motor (MongoDB), port 8001, routes prefixed /api
- Frontend: React + Tailwind, port 3000
- Logs: /var/log/supervisor/backend.err.log, /var/log/supervisor/frontend.err.log
- DB: MongoDB at MONGO_URL from backend/.env
- Common issues: ObjectId serialization, missing _id exclusion, import errors, env var typos, CORS
"""


# ═══════════════════════════════════════════════════════════
# UNIFIED SUBAGENT CALLER
# ═══════════════════════════════════════════════════════════

async def call_subagent(agent_type: str, task: str, context: str = "", run_tests: bool = False) -> dict:
    """Call a specialized subagent with focused task. Optionally run tests for tester agent."""
    prompts = {
        "tester": TESTER_V3_PROMPT,
        "designer": DESIGNER_V2_PROMPT,
        "integrator": INTEGRATOR_V2_PROMPT,
        "troubleshooter": TROUBLESHOOTER_V2_PROMPT,
    }

    system = prompts.get(agent_type)
    if not system:
        return {"status": "error", "error": f"Unknown agent_type: {agent_type}. Use: tester, designer, integrator, troubleshooter"}

    # For integrator, inject verified playbook if available
    if agent_type == "integrator":
        task_lower = task.lower()
        for key, playbook in VERIFIED_PLAYBOOKS.items():
            if key in task_lower:
                system += f"\n\n## VERIFIED PLAYBOOK for {playbook['name']}:\n```json\n{json.dumps(playbook, indent=2, default=str)}\n```\nUse this verified playbook as the base for your response."
                break

    key = _get_key()
    if not key:
        return {"status": "error", "error": "No LLM key configured. Set EMERGENT_LLM_KEY in backend/.env"}

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

        result = {
            "status": "ok",
            "agent_type": agent_type,
            "response": response[:15000],
            "full_length": len(response),
        }

        # For tester agent: optionally parse and run the tests
        if agent_type == "tester" and run_tests:
            try:
                # Try to extract JSON test suite from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    test_suite = json.loads(response[json_start:json_end])
                    tests_to_run = []

                    for bt in test_suite.get("backend_tests", []):
                        tests_to_run.append({"id": bt.get("id", "?"), "name": bt.get("name", "?"), "type": bt.get("type", "curl"), "command": bt.get("command", "")})

                    for ft in test_suite.get("frontend_tests", []):
                        tests_to_run.append({"id": ft.get("id", "?"), "name": ft.get("name", "?"), "type": "playwright", "script": ft.get("playwright_script", "pass")})

                    if tests_to_run:
                        report = await run_test_suite(tests_to_run)
                        result["test_report"] = report
                        result["test_report_path"] = report.get("report_path")
            except (json.JSONDecodeError, KeyError) as e:
                result["test_parse_error"] = f"Could not parse test suite: {str(e)}"

        return result
    except Exception as e:
        logger.error(f"Subagent {agent_type} failed: {traceback.format_exc()}")
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
            img_id = str(uuid.uuid4())[:8]
            img_path = f"/app/backend/uploads/generated_{img_id}.png"
            os.makedirs("/app/backend/uploads", exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(images[0])

            image_base64 = b64.b64encode(images[0]).decode('utf-8')
            file_size = len(images[0])

            return {
                "status": "ok",
                "prompt": prompt,
                "path": img_path,
                "image_url": f"data:image/png;base64,{image_base64[:100]}...",
                "file_size_kb": round(file_size / 1024, 1),
                "serve_url": f"/api/agents/screenshots/generated_{img_id}.png",
            }
        else:
            return {"status": "error", "error": "No image was generated"}
    except Exception as e:
        return {"status": "error", "error": f"Image generation failed: {str(e)}"}


def _indent(code: str, spaces: int) -> str:
    """Indent a block of code by N spaces."""
    prefix = ' ' * spaces
    return '\n'.join(prefix + line for line in code.split('\n'))

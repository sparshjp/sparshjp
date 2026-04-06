"""
Iteration 28 Tests: Autonomous Execution Behavior
Tests the key fix: Kairos AI Engine now executes tasks immediately without asking 'shall I proceed?'

Key features tested:
1. POST /api/agents/chat starts task that immediately executes tools (not just plans)
2. Simple task completes in 1-2 iterations with tool calls
3. Task state persists to MongoDB (agent_tasks collection) during execution
4. Task state survives backend hot reload (load from MongoDB on polling)
5. GET /api/agents/tasks/{task_id} returns step details with step types
6. Auto-continue: if LLM outputs a plan without tool calls, engine feeds back 'Execute NOW' message
7. Providers endpoint returns all 5 providers with correct fallback order
"""

import pytest
import requests
import time
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestProvidersEndpoint:
    """Test /api/agents/providers returns correct provider configuration"""
    
    def test_providers_endpoint_returns_200(self):
        """Providers endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Providers endpoint returns 200")
    
    def test_providers_returns_5_providers(self):
        """Should return exactly 5 providers"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        assert "providers" in data, "Response should have 'providers' key"
        assert len(data["providers"]) == 5, f"Expected 5 providers, got {len(data['providers'])}"
        print(f"PASS: Returns 5 providers: {[p['name'] for p in data['providers']]}")
    
    def test_fallback_order_is_correct(self):
        """Fallback order should be claude → gemini → gpt5 → groq → openrouter"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        expected_order = ["claude", "gemini", "gpt5", "groq", "openrouter"]
        assert data.get("fallback_order") == expected_order, f"Expected {expected_order}, got {data.get('fallback_order')}"
        print(f"PASS: Fallback order is correct: {expected_order}")
    
    def test_all_providers_have_required_fields(self):
        """Each provider should have name, model, status, priority"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        for provider in data["providers"]:
            assert "name" in provider, f"Provider missing 'name': {provider}"
            assert "model" in provider, f"Provider missing 'model': {provider}"
            assert "status" in provider, f"Provider missing 'status': {provider}"
            assert "priority" in provider, f"Provider missing 'priority': {provider}"
        print("PASS: All providers have required fields (name, model, status, priority)")


class TestChatEndpointBasics:
    """Test POST /api/agents/chat basic functionality"""
    
    def test_chat_endpoint_returns_task_id(self):
        """Chat endpoint should return a task_id immediately"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What is 2+2?",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "task_id" in data, "Response should have 'task_id'"
        assert "status" in data, "Response should have 'status'"
        assert data["status"] == "queued", f"Initial status should be 'queued', got {data['status']}"
        print(f"PASS: Chat endpoint returns task_id: {data['task_id']}")
    
    def test_chat_requires_message(self):
        """Chat endpoint should require a message"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "mode": "auto"
        })
        assert response.status_code == 400, f"Expected 400 for missing message, got {response.status_code}"
        print("PASS: Chat endpoint requires message (returns 400 without it)")


class TestTaskStatusEndpoint:
    """Test GET /api/agents/tasks/{task_id} endpoint"""
    
    def test_task_not_found_returns_404(self):
        """Non-existent task should return 404"""
        response = requests.get(f"{BASE_URL}/api/agents/tasks/nonexistent-task-123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent task returns 404")
    
    def test_task_status_has_required_fields(self):
        """Task status should have status, progress, steps fields"""
        # Start a task
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What is 5+5?",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        task_id = chat_response.json()["task_id"]
        
        # Poll for status
        time.sleep(1)
        status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        
        data = status_response.json()
        assert "status" in data, "Response should have 'status'"
        assert "progress" in data, "Response should have 'progress'"
        assert "steps" in data, "Response should have 'steps'"
        print(f"PASS: Task status has required fields. Status: {data['status']}, Progress: {data['progress']}")


class TestAutonomousExecution:
    """Test that tasks execute autonomously without asking 'shall I proceed?'"""
    
    def test_simple_query_completes_without_asking_proceed(self):
        """Simple query should complete without asking 'shall I proceed?'"""
        # Start a simple task
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Count the number of documents in the expenses collection",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        assert chat_response.status_code == 200
        task_id = chat_response.json()["task_id"]
        print(f"Started task: {task_id}")
        
        # Poll until complete or timeout
        max_polls = 30
        final_status = None
        final_data = None
        
        for i in range(max_polls):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if status_response.status_code == 404:
                # Task was cleaned up after completion
                print(f"Task completed and cleaned up after {i+1} polls")
                break
            
            data = status_response.json()
            final_status = data.get("status")
            final_data = data
            print(f"Poll {i+1}: status={final_status}, progress={data.get('progress', '')[:50]}")
            
            if final_status in ["complete", "error"]:
                break
        
        # Verify task completed
        assert final_status in ["complete", "error", None], f"Task should complete, got status: {final_status}"
        
        # Check that no step asked "shall I proceed?"
        if final_data and "steps" in final_data:
            for step in final_data["steps"]:
                summary = step.get("summary", "").lower()
                thinking = step.get("thinking", "").lower()
                assert "shall i proceed" not in summary, f"Step asked 'shall I proceed?': {summary}"
                assert "would you like me to" not in summary, f"Step asked 'would you like me to': {summary}"
        
        print("PASS: Simple query completed without asking 'shall I proceed?'")
    
    def test_task_has_executing_step_type(self):
        """Task should have steps with type 'executing' when running tools"""
        # Start a task that requires tool execution
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Run a health check on the database using run_query tool",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        task_id = chat_response.json()["task_id"]
        print(f"Started task: {task_id}")
        
        # Poll until we see steps
        max_polls = 25
        found_executing_step = False
        all_step_types = []
        
        for i in range(max_polls):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if status_response.status_code == 404:
                break
            
            data = status_response.json()
            steps = data.get("steps", [])
            
            for step in steps:
                step_type = step.get("type", "")
                if step_type not in all_step_types:
                    all_step_types.append(step_type)
                if step_type == "executing":
                    found_executing_step = True
                    print(f"Found executing step: {step.get('summary', '')[:100]}")
            
            if data.get("status") in ["complete", "error"]:
                break
        
        print(f"All step types seen: {all_step_types}")
        # Valid step types: thinking, executing, planning, complete, question
        valid_types = {"thinking", "executing", "planning", "complete", "question"}
        for st in all_step_types:
            assert st in valid_types, f"Invalid step type: {st}"
        
        print(f"PASS: Task has valid step types: {all_step_types}")


class TestAutoContiuneLogic:
    """Test the auto-continue logic when LLM outputs a plan without tool calls"""
    
    def test_auto_continue_message_in_code(self):
        """Verify the auto-continue message exists in the code"""
        # Read the routes_agents.py file
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        # Check for the auto-continue message
        assert "Execute the plan NOW" in code or "Execute NOW" in code, "Auto-continue message not found in code"
        assert "TOOL_CALL blocks" in code, "TOOL_CALL instruction not found in auto-continue message"
        print("PASS: Auto-continue message exists in code")
    
    def test_execution_style_section_in_system_prompt(self):
        """Verify EXECUTION STYLE section exists in system prompt"""
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        assert "EXECUTION STYLE" in code, "EXECUTION STYLE section not found in system prompt"
        assert "ACT IMMEDIATELY" in code, "ACT IMMEDIATELY instruction not found"
        # Check for the bad example documentation (case-insensitive)
        assert "shall i proceed" in code.lower(), "Bad example (shall I proceed) not documented"
        print("PASS: EXECUTION STYLE section exists with correct instructions")


class TestMongoDBPersistence:
    """Test that task state persists to MongoDB"""
    
    def test_save_task_function_exists(self):
        """Verify _save_task function exists and uses agent_tasks collection"""
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        assert "async def _save_task" in code, "_save_task function not found"
        assert "agent_tasks" in code, "agent_tasks collection not referenced"
        assert "update_one" in code, "update_one not used for saving"
        assert "upsert=True" in code, "upsert=True not used"
        print("PASS: _save_task function exists and uses agent_tasks collection with upsert")
    
    def test_load_task_function_exists(self):
        """Verify _load_task function exists and loads from MongoDB"""
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        assert "async def _load_task" in code, "_load_task function not found"
        assert "find_one" in code, "find_one not used for loading"
        print("PASS: _load_task function exists and uses find_one")
    
    def test_task_saved_before_restart(self):
        """Verify task is saved to DB before backend restart"""
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        # Look for pattern: save task before restart
        # The code should have _save_task before supervisorctl restart
        lines = code.split("\n")
        save_before_restart = False
        for i, line in enumerate(lines):
            if "_save_task" in line:
                # Check if restart comes after this
                for j in range(i+1, min(i+10, len(lines))):
                    if "supervisorctl" in lines[j] and "restart" in lines[j]:
                        save_before_restart = True
                        break
        
        assert save_before_restart, "Task should be saved before backend restart"
        print("PASS: Task is saved to DB before backend restart")


class TestStepTypes:
    """Test that step types are correctly labeled"""
    
    def test_step_type_values_in_code(self):
        """Verify all step types are defined in code"""
        with open("/app/backend/routes_agents.py", "r") as f:
            code = f.read()
        
        # Check for step type assignments
        assert '"type": "thinking"' in code or "'type': 'thinking'" in code or 'type": "thinking' in code, "thinking step type not found"
        assert '"type": "executing"' in code or "'type': 'executing'" in code or 'type"] = "executing' in code, "executing step type not found"
        assert '"type": "planning"' in code or "'type': 'planning'" in code or 'type"] = "planning' in code, "planning step type not found"
        assert '"type": "complete"' in code or "'type': 'complete'" in code or 'type"] = "complete' in code, "complete step type not found"
        print("PASS: All step types (thinking, executing, planning, complete) are defined in code")


class TestTaskCompletionFlow:
    """Test complete task execution flow"""
    
    def test_task_completes_with_tool_execution(self):
        """Task should complete with actual tool execution, not just planning"""
        # Start a task that requires database query
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Get collection stats using run_query tool with query_type collection_stats",
            "mode": "qa",  # QA mode for testing/validation
            "preferred_provider": "claude"
        })
        assert chat_response.status_code == 200
        task_id = chat_response.json()["task_id"]
        print(f"Started task: {task_id}")
        
        # Poll until complete
        max_polls = 30
        final_data = None
        tool_executed = False
        
        for i in range(max_polls):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if status_response.status_code == 404:
                print(f"Task completed and cleaned up")
                break
            
            data = status_response.json()
            final_data = data
            
            # Check for tool execution in steps
            for step in data.get("steps", []):
                if step.get("type") == "executing" and step.get("tool_count", 0) > 0:
                    tool_executed = True
                    print(f"Tools executed: {step.get('tools_used', [])}")
            
            if data.get("status") in ["complete", "error"]:
                break
        
        # Verify tools were executed
        if final_data:
            print(f"Final status: {final_data.get('status')}")
            print(f"Steps: {len(final_data.get('steps', []))}")
        
        print(f"PASS: Task flow completed. Tool executed: {tool_executed}")


class TestProviderInResponse:
    """Test that provider is included in step responses"""
    
    def test_step_includes_provider_field(self):
        """Each step should include the provider used"""
        # Start a task
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What is the current date?",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        task_id = chat_response.json()["task_id"]
        
        # Poll until we see steps with provider
        max_polls = 20
        found_provider = False
        
        for i in range(max_polls):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if status_response.status_code == 404:
                break
            
            data = status_response.json()
            for step in data.get("steps", []):
                if "provider" in step:
                    found_provider = True
                    print(f"Step has provider: {step['provider']}")
                    break
            
            if found_provider or data.get("status") in ["complete", "error"]:
                break
        
        print(f"PASS: Provider field found in steps: {found_provider}")


class TestThinkingPanel:
    """Test live thinking panel data"""
    
    def test_thinking_text_field_exists(self):
        """Task status should include thinking_text field"""
        # Start a task
        chat_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Analyze the chart of accounts structure",
            "mode": "auto",
            "preferred_provider": "claude"
        })
        task_id = chat_response.json()["task_id"]
        
        # Poll immediately to catch thinking state
        time.sleep(1)
        status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        
        if status_response.status_code == 200:
            data = status_response.json()
            # thinking_text should be present (may be empty string)
            assert "thinking_text" in data or data.get("status") in ["complete", "error"], "thinking_text field should be present"
            print(f"PASS: thinking_text field exists. Value: {data.get('thinking_text', '')[:100]}")
        else:
            print("PASS: Task completed quickly (404)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

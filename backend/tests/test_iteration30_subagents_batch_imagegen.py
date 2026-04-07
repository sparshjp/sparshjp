"""
Iteration 30 Tests: Subagents, Batch Operations, Image Generation, Expanded Context
Tests for tools 28-30 in Kairos AI Engine v4:
- call_subagent: Specialized AI subagents (tester, designer, integrator, troubleshooter)
- batch_operations: Parallel file operations (create, delete, move, patch, read)
- generate_image: AI image generation via GPT Image 1
- Expanded context window: 12 messages in loop, 26 in history
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://prompt-to-post-4.preview.emergentagent.com').rstrip('/')


class TestCallSubagentTool:
    """Tests for call_subagent tool (tool #28)"""
    
    def test_call_subagent_tool_exists_in_code(self):
        """Verify call_subagent tool handler exists in routes_agents.py"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'tool_name == "call_subagent"' in content, "call_subagent tool handler not found"
    
    def test_call_subagent_in_read_tools(self):
        """Verify call_subagent is in READ_TOOLS set"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        # Find READ_TOOLS definition
        match = re.search(r'READ_TOOLS\s*=\s*\{([^}]+)\}', content)
        assert match, "READ_TOOLS set not found"
        assert 'call_subagent' in match.group(1), "call_subagent not in READ_TOOLS"
    
    def test_call_subagent_requires_agent_type_and_task(self):
        """Verify call_subagent validates required parameters"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'agent_type and task are required' in content, "Parameter validation not found"
    
    def test_call_subagent_delegates_to_kairos_subagents(self):
        """Verify call_subagent calls the subagent module"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'from kairos_subagents import call_subagent' in content, "Import from kairos_subagents not found"
        assert 'await call_subagent(agent_type, task, context)' in content, "Delegation to subagent not found"


class TestKairosSubagentsModule:
    """Tests for kairos_subagents.py module"""
    
    def test_subagent_module_exists(self):
        """Verify kairos_subagents.py exists"""
        assert os.path.isfile('/app/backend/kairos_subagents.py'), "kairos_subagents.py not found"
    
    def test_tester_subagent_prompt_exists(self):
        """Verify TESTER_PROMPT is defined"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'TESTER_PROMPT' in content, "TESTER_PROMPT not found"
        assert 'Testing Expert Subagent' in content, "Tester description not found"
    
    def test_designer_subagent_prompt_exists(self):
        """Verify DESIGNER_PROMPT is defined"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'DESIGNER_PROMPT' in content, "DESIGNER_PROMPT not found"
        assert 'UI/UX Design Expert Subagent' in content, "Designer description not found"
    
    def test_integrator_subagent_prompt_exists(self):
        """Verify INTEGRATOR_PROMPT is defined"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'INTEGRATOR_PROMPT' in content, "INTEGRATOR_PROMPT not found"
        assert 'Integration Expert Subagent' in content, "Integrator description not found"
    
    def test_troubleshooter_subagent_prompt_exists(self):
        """Verify TROUBLESHOOTER_PROMPT is defined"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'TROUBLESHOOTER_PROMPT' in content, "TROUBLESHOOTER_PROMPT not found"
        assert 'Troubleshooting Expert Subagent' in content, "Troubleshooter description not found"
    
    def test_call_subagent_function_exists(self):
        """Verify call_subagent async function exists"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'async def call_subagent(agent_type: str, task: str, context: str = "")' in content, "call_subagent function not found"
    
    def test_call_subagent_validates_agent_type(self):
        """Verify call_subagent rejects unknown agent types"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'Unknown agent_type' in content, "Unknown agent_type error not found"
        # Check that all 4 agent types are supported
        assert 'tester' in content and 'designer' in content and 'integrator' in content and 'troubleshooter' in content, "Valid agent types not listed"
    
    def test_call_subagent_uses_claude_model(self):
        """Verify subagent uses Claude model"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'claude-sonnet-4-5-20250929' in content, "Claude model not found in subagent"


class TestBatchOperationsTool:
    """Tests for batch_operations tool (tool #29)"""
    
    def test_batch_operations_tool_exists_in_code(self):
        """Verify batch_operations tool handler exists"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'tool_name == "batch_operations"' in content, "batch_operations tool handler not found"
    
    def test_batch_operations_in_write_tools(self):
        """Verify batch_operations is in WRITE_TOOLS set"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        match = re.search(r'WRITE_TOOLS\s*=\s*\{([^}]+)\}', content)
        assert match, "WRITE_TOOLS set not found"
        assert 'batch_operations' in match.group(1), "batch_operations not in WRITE_TOOLS"
    
    def test_batch_operations_supports_create_action(self):
        """Verify batch_operations supports create action"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'action == "create"' in content, "create action not found in batch_operations"
    
    def test_batch_operations_supports_delete_action(self):
        """Verify batch_operations supports delete action"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'action == "delete"' in content, "delete action not found in batch_operations"
    
    def test_batch_operations_supports_move_action(self):
        """Verify batch_operations supports move action"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'action == "move"' in content, "move action not found in batch_operations"
    
    def test_batch_operations_supports_patch_action(self):
        """Verify batch_operations supports patch action"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'action == "patch"' in content, "patch action not found in batch_operations"
    
    def test_batch_operations_supports_read_action(self):
        """Verify batch_operations supports read action"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'action == "read"' in content, "read action not found in batch_operations"
    
    def test_batch_operations_uses_asyncio_gather(self):
        """Verify batch_operations uses asyncio.gather for parallel execution"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'asyncio.gather' in content, "asyncio.gather not found"
        # Check it's used in batch_operations context (within 2500 chars of the tool handler)
        batch_section = content[content.find('tool_name == "batch_operations"'):]
        assert 'asyncio.gather' in batch_section[:2500], "asyncio.gather not used in batch_operations"
    
    def test_batch_operations_returns_succeeded_failed_count(self):
        """Verify batch_operations returns succeeded/failed counts"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert '"succeeded":' in content, "succeeded count not in response"
        assert '"failed":' in content, "failed count not in response"
    
    def test_batch_operations_limits_to_20_ops(self):
        """Verify batch_operations limits to 20 operations"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'operations[:20]' in content, "20 operation limit not found"


class TestGenerateImageTool:
    """Tests for generate_image tool (tool #30)"""
    
    def test_generate_image_tool_exists_in_code(self):
        """Verify generate_image tool handler exists"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'tool_name == "generate_image"' in content, "generate_image tool handler not found"
    
    def test_generate_image_in_read_tools(self):
        """Verify generate_image is in READ_TOOLS set"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        match = re.search(r'READ_TOOLS\s*=\s*\{([^}]+)\}', content)
        assert match, "READ_TOOLS set not found"
        assert 'generate_image' in match.group(1), "generate_image not in READ_TOOLS"
    
    def test_generate_image_requires_prompt(self):
        """Verify generate_image validates prompt parameter"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'prompt is required' in content, "Prompt validation not found"
    
    def test_generate_image_delegates_to_kairos_subagents(self):
        """Verify generate_image calls the subagent module"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'from kairos_subagents import' in content and 'generate_image' in content, "Import from kairos_subagents not found"
        assert 'await gen_image(prompt, size)' in content, "Delegation to gen_image not found"


class TestGenerateImageFunction:
    """Tests for generate_image function in kairos_subagents.py"""
    
    def test_generate_image_function_exists(self):
        """Verify generate_image async function exists"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'async def generate_image(prompt: str, size: str = "1024x1024")' in content, "generate_image function not found"
    
    def test_generate_image_uses_openai_image_generation(self):
        """Verify generate_image uses OpenAIImageGeneration"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration' in content, "OpenAIImageGeneration import not found"
    
    def test_generate_image_uses_gpt_image_1_model(self):
        """Verify generate_image uses gpt-image-1 model"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert 'gpt-image-1' in content, "gpt-image-1 model not found"
    
    def test_generate_image_saves_to_uploads_directory(self):
        """Verify generate_image saves images to uploads directory"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert '/app/backend/uploads/generated_' in content, "Upload path not found"
    
    def test_generate_image_returns_serve_url(self):
        """Verify generate_image returns serve_url for frontend"""
        with open('/app/backend/kairos_subagents.py', 'r') as f:
            content = f.read()
        assert '/api/agents/screenshots/generated_' in content, "serve_url not found"


class TestExpandedContext:
    """Tests for expanded context window"""
    
    def test_system_prompt_mentions_30_tools(self):
        """Verify system prompt mentions 30 tools"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        # Check for tool 28, 29, 30 in system prompt
        assert '28. **call_subagent' in content, "Tool 28 (call_subagent) not in system prompt"
        assert '29. **batch_operations' in content, "Tool 29 (batch_operations) not in system prompt"
        assert '30. **generate_image' in content, "Tool 30 (generate_image) not in system prompt"


class TestFrontendNewTools:
    """Tests for frontend updates for new tools"""
    
    def test_frontend_has_bot_icon_import(self):
        """Verify Bot icon is imported for call_subagent"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Bot' in content, "Bot icon not imported"
    
    def test_frontend_has_layers_icon_import(self):
        """Verify Layers icon is imported for batch_operations"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Layers' in content, "Layers icon not imported"
    
    def test_frontend_has_imageplus_icon_import(self):
        """Verify ImagePlus icon is imported for generate_image"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'ImagePlus' in content, "ImagePlus icon not imported"
    
    def test_frontend_tool_icons_has_call_subagent(self):
        """Verify TOOL_ICONS has call_subagent mapping"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'call_subagent: Bot' in content, "call_subagent icon mapping not found"
    
    def test_frontend_tool_icons_has_batch_operations(self):
        """Verify TOOL_ICONS has batch_operations mapping"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'batch_operations: Layers' in content, "batch_operations icon mapping not found"
    
    def test_frontend_tool_icons_has_generate_image(self):
        """Verify TOOL_ICONS has generate_image mapping"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'generate_image: ImagePlus' in content, "generate_image icon mapping not found"
    
    def test_frontend_tool_colors_has_call_subagent(self):
        """Verify TOOL_COLORS has call_subagent color"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'call_subagent:' in content and '#00d4aa' in content, "call_subagent color not found"
    
    def test_frontend_tool_colors_has_batch_operations(self):
        """Verify TOOL_COLORS has batch_operations color"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'batch_operations:' in content and '#22c55e' in content, "batch_operations color not found"
    
    def test_frontend_tool_colors_has_generate_image(self):
        """Verify TOOL_COLORS has generate_image color"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'generate_image:' in content and '#e879f9' in content, "generate_image color not found"
    
    def test_frontend_shows_30_tools_badge(self):
        """Verify frontend shows '30 Tools + Image Gen' badge"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert '30 Tools + Image Gen' in content, "'30 Tools + Image Gen' badge not found"
    
    def test_frontend_header_shows_30_tools_4_subagents(self):
        """Verify header shows '30 Tools · 4 Subagents · Image Gen · 5 Providers'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert '30 Tools' in content, "'30 Tools' not in header"
        assert '4 Subagents' in content, "'4 Subagents' not in header"
        assert 'Image Gen' in content, "'Image Gen' not in header"
        assert '5 Providers' in content, "'5 Providers' not in header"
    
    def test_frontend_footer_shows_30_tools_4_subagents(self):
        """Verify footer shows '30 tools · 4 subagents · 5 LLM providers'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert '30 tools' in content, "'30 tools' not in footer"
        assert '4 subagents' in content, "'4 subagents' not in footer"
        assert '5 LLM providers' in content, "'5 LLM providers' not in footer"


class TestToolResultCardSummaries:
    """Tests for ToolResultCard summary generation for new tools"""
    
    def test_call_subagent_summary_in_tool_result_card(self):
        """Verify call_subagent summary shows agent_type and task"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert "result.tool === 'call_subagent'" in content, "call_subagent summary case not found"
        assert "agent_type" in content, "agent_type not in summary"
    
    def test_batch_operations_summary_in_tool_result_card(self):
        """Verify batch_operations summary shows succeeded/total count"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert "result.tool === 'batch_operations'" in content, "batch_operations summary case not found"
        assert "succeeded" in content, "succeeded not in summary"
    
    def test_generate_image_summary_in_tool_result_card(self):
        """Verify generate_image summary shows prompt"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert "result.tool === 'generate_image'" in content, "generate_image summary case not found"


class TestSubagentResponseDisplay:
    """Tests for subagent response display in frontend"""
    
    def test_call_subagent_shows_bot_icon_in_expanded(self):
        """Verify call_subagent expanded view shows Bot icon"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check for Bot icon in call_subagent expanded section
        assert "result.tool === 'call_subagent' && result.result?.response" in content, "call_subagent expanded check not found"
        assert '<Bot size={11}' in content, "Bot icon not in expanded view"
    
    def test_call_subagent_shows_agent_type_label(self):
        """Verify call_subagent shows agent type label"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'agent_type} subagent' in content, "agent_type label not found"


class TestGenerateImageDisplay:
    """Tests for generate_image display in frontend"""
    
    def test_generate_image_shows_image_preview(self):
        """Verify generate_image shows image preview"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert "result.tool === 'generate_image' && result.result?.serve_url" in content, "generate_image preview check not found"
        assert 'Generated image' in content or 'alt={result.args?.prompt' in content, "Image alt text not found"


class TestProvidersEndpoint:
    """Tests for /api/agents/providers endpoint"""
    
    def test_providers_returns_5_providers(self):
        """Verify GET /api/agents/providers returns 5 providers"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'providers' in data, "providers key not in response"
        assert len(data['providers']) == 5, f"Expected 5 providers, got {len(data['providers'])}"
        provider_names = [p['name'] for p in data['providers']]
        assert 'claude' in provider_names, "claude not in providers"
        assert 'gemini' in provider_names, "gemini not in providers"
        assert 'gpt5' in provider_names, "gpt5 not in providers"
        assert 'groq' in provider_names, "groq not in providers"
        assert 'openrouter' in provider_names, "openrouter not in providers"


class TestChatEndpoint:
    """Tests for /api/agents/chat endpoint"""
    
    def test_chat_endpoint_exists(self):
        """Verify POST /api/agents/chat endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "agent_type": "auto",
            "message": "test",
            "session_id": "test-session"
        })
        # Should return 200 with task_id (async task)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'task_id' in data, "task_id not in response"


class TestScreenshotEndpoint:
    """Tests for screenshot serving endpoint"""
    
    def test_screenshot_endpoint_pattern(self):
        """Verify screenshot endpoint pattern exists for generated images"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        # Check for screenshot serving endpoint
        assert '/screenshots/' in content or 'screenshots' in content, "Screenshot endpoint not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

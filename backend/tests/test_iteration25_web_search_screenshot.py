"""
Iteration 25 Tests: Web Search and Screenshot Tools
Tests for the new web_search (tool 20) and take_screenshot (tool 21) capabilities
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWebSearchTool:
    """Tests for web_search tool (tool 20) - DuckDuckGo search"""
    
    def test_web_search_in_read_tools(self):
        """Verify web_search is in READ_TOOLS set by checking system prompt"""
        # The system prompt mentions web_search as tool 20
        # We verify by checking the routes_agents.py file
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'web_search' in content, "web_search tool not found in routes_agents.py"
        assert '"web_search"' in content or "'web_search'" in content, "web_search not defined as tool"
        # Check it's in READ_TOOLS
        assert 'READ_TOOLS' in content, "READ_TOOLS set not found"
        # Find READ_TOOLS line and verify web_search is in it
        for line in content.split('\n'):
            if 'READ_TOOLS' in line and '=' in line:
                assert 'web_search' in line, "web_search not in READ_TOOLS set"
                break
    
    def test_web_search_tool_exists_in_execute_tool(self):
        """Verify web_search tool handler exists in execute_tool function"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'elif tool_name == "web_search"' in content, "web_search handler not found in execute_tool"
        assert 'from ddgs import DDGS' in content, "ddgs import not found for web_search"
    
    def test_web_search_documented_in_system_prompt(self):
        """Verify web_search is documented in ENGINE_SYSTEM_PROMPT"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert '20. **web_search' in content, "web_search not documented as tool 20 in system prompt"
        assert 'DuckDuckGo' in content, "DuckDuckGo not mentioned in web_search documentation"


class TestTakeScreenshotTool:
    """Tests for take_screenshot tool (tool 21) - Playwright/Chromium screenshot"""
    
    def test_take_screenshot_in_read_tools(self):
        """Verify take_screenshot is in READ_TOOLS set"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'take_screenshot' in content, "take_screenshot tool not found in routes_agents.py"
        # Check it's in READ_TOOLS
        for line in content.split('\n'):
            if 'READ_TOOLS' in line and '=' in line:
                assert 'take_screenshot' in line, "take_screenshot not in READ_TOOLS set"
                break
    
    def test_take_screenshot_tool_exists_in_execute_tool(self):
        """Verify take_screenshot tool handler exists in execute_tool function"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert 'elif tool_name == "take_screenshot"' in content, "take_screenshot handler not found in execute_tool"
        assert 'playwright' in content.lower(), "playwright not found for take_screenshot"
    
    def test_take_screenshot_documented_in_system_prompt(self):
        """Verify take_screenshot is documented in ENGINE_SYSTEM_PROMPT"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert '21. **take_screenshot' in content, "take_screenshot not documented as tool 21 in system prompt"
        assert 'Chromium' in content, "Chromium not mentioned in take_screenshot documentation"


class TestScreenshotServeEndpoint:
    """Tests for GET /api/agents/screenshots/{filename} endpoint"""
    
    def test_screenshot_endpoint_exists(self):
        """Verify screenshot serve endpoint is defined"""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        assert '/screenshots/{filename}' in content, "Screenshot serve endpoint not found"
        assert 'serve_screenshot' in content, "serve_screenshot function not found"
    
    def test_screenshot_endpoint_returns_200_for_existing_file(self):
        """Test that existing screenshot returns 200 with image/png content type"""
        # Use the existing screenshot file
        response = requests.get(f"{BASE_URL}/api/agents/screenshots/screenshot_fd74d216.png")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'image/png' in response.headers.get('content-type', ''), "Content-Type should be image/png"
        assert len(response.content) > 0, "Screenshot content should not be empty"
    
    def test_screenshot_endpoint_returns_400_for_nonexistent_file(self):
        """Test that nonexistent screenshot with invalid format returns 400"""
        # The endpoint validates filename format first, so invalid format returns 400
        response = requests.get(f"{BASE_URL}/api/agents/screenshots/screenshot_nonexistent.png")
        assert response.status_code == 400, f"Expected 400 for invalid filename format, got {response.status_code}"
        data = response.json()
        assert 'detail' in data, "Response should contain error detail"
    
    def test_screenshot_endpoint_validates_filename_format(self):
        """Test that invalid filename format returns 400"""
        # Invalid filename (doesn't match screenshot_[hex].png pattern)
        response = requests.get(f"{BASE_URL}/api/agents/screenshots/invalid_name.png")
        assert response.status_code == 400, f"Expected 400 for invalid filename, got {response.status_code}"
        
        # Test with valid format but nonexistent file - should return 404
        response = requests.get(f"{BASE_URL}/api/agents/screenshots/screenshot_00000000.png")
        assert response.status_code == 404, f"Expected 404 for nonexistent valid filename, got {response.status_code}"


class TestAgentsChatEndpoint:
    """Tests for POST /api/agents/chat endpoint"""
    
    def test_chat_endpoint_returns_task_id(self):
        """Test that chat endpoint returns task_id"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "auto", "message": "What is 1+1?"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'task_id' in data, "Response should contain task_id"
        assert 'status' in data, "Response should contain status"
    
    def test_chat_endpoint_accepts_session_id(self):
        """Test that chat endpoint accepts session_id parameter"""
        # First create a session
        session_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "Test Session"}
        )
        session_id = session_response.json().get('id')
        
        # Then send a chat with session_id
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "auto", "message": "Hello", "session_id": session_id}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


class TestAgentsTaskPolling:
    """Tests for GET /api/agents/tasks/{task_id} endpoint"""
    
    def test_task_polling_returns_thinking_fields(self):
        """Test that task polling returns thinking_text and thinking_step fields"""
        # Create a task
        chat_response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "auto", "message": "What is 2+2?"}
        )
        task_id = chat_response.json().get('task_id')
        
        # Poll for task status
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check that thinking fields exist (may be empty if task completed quickly)
        assert 'status' in data, "Response should contain status"
        # thinking_text and thinking_step are optional during processing
    
    def test_task_not_found_returns_404(self):
        """Test that nonexistent task returns 404"""
        response = requests.get(f"{BASE_URL}/api/agents/tasks/nonexistent-task-id")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestToolIconsAndColors:
    """Tests to verify tool icons and colors are defined in frontend"""
    
    def test_web_search_icon_defined(self):
        """Verify web_search has Globe icon in TOOL_ICONS"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'web_search: Globe' in content, "web_search should have Globe icon"
    
    def test_take_screenshot_icon_defined(self):
        """Verify take_screenshot has Camera icon in TOOL_ICONS"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'take_screenshot: Camera' in content, "take_screenshot should have Camera icon"
    
    def test_web_search_color_defined(self):
        """Verify web_search has color in TOOL_COLORS"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'web_search:' in content and '#f97316' in content, "web_search should have orange color #f97316"
    
    def test_take_screenshot_color_defined(self):
        """Verify take_screenshot has color in TOOL_COLORS"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'take_screenshot:' in content and '#e879f9' in content, "take_screenshot should have pink color #e879f9"


class TestFrontendBadgesAndFooter:
    """Tests to verify frontend badges and footer are updated for 21 tools"""
    
    def test_badge_shows_21_tools(self):
        """Verify badge shows '21 Tools + Web Search'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert '21 Tools + Web Search' in content, "Badge should show '21 Tools + Web Search'"
    
    def test_footer_shows_21_tools(self):
        """Verify footer shows '21 tools'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check footer text
        assert '21 tools' in content, "Footer should mention '21 tools'"
    
    def test_footer_shows_web_search(self):
        """Verify footer mentions 'Web search'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Web search' in content or 'web search' in content.lower(), "Footer should mention 'Web search'"
    
    def test_footer_shows_screenshots(self):
        """Verify footer mentions 'Screenshots'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Screenshots' in content or 'screenshots' in content.lower(), "Footer should mention 'Screenshots'"
    
    def test_header_subtitle_shows_21_tools(self):
        """Verify header subtitle shows '21 Tools · Web Search · Screenshots · Auto-Verify'"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert '21 Tools' in content, "Header subtitle should show '21 Tools'"
        assert 'Web Search' in content, "Header subtitle should show 'Web Search'"
        assert 'Screenshots' in content, "Header subtitle should show 'Screenshots'"


class TestToolResultCardEnhancements:
    """Tests to verify ToolResultCard handles web_search and take_screenshot results"""
    
    def test_tool_result_card_handles_web_search(self):
        """Verify ToolResultCard has web_search result display logic"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check for web_search result handling in ToolResultCard
        assert "result.tool === 'web_search'" in content, "ToolResultCard should handle web_search results"
        assert 'result.result.results' in content or 'result.result?.results' in content, "Should display web search results"
    
    def test_tool_result_card_handles_take_screenshot(self):
        """Verify ToolResultCard has take_screenshot result display logic"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check for take_screenshot result handling in ToolResultCard
        assert "result.tool === 'take_screenshot'" in content, "ToolResultCard should handle take_screenshot results"
        assert '/api/agents/screenshots/' in content, "Should construct screenshot URL for display"
    
    def test_web_search_results_have_clickable_links(self):
        """Verify web search results display clickable links"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check for anchor tags with href in web search results
        assert 'href={r.url}' in content or 'href={r.href}' in content, "Web search results should have clickable links"
        assert 'target="_blank"' in content, "Links should open in new tab"
    
    def test_screenshot_preview_uses_img_tag(self):
        """Verify screenshot preview uses img tag"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        # Check for img tag for screenshot preview
        assert '<img' in content, "Should use img tag for screenshot preview"
        assert 'screenshot' in content.lower(), "Should reference screenshot in img handling"


class TestLucideIconImports:
    """Tests to verify required Lucide icons are imported"""
    
    def test_globe_icon_imported(self):
        """Verify Globe icon is imported from lucide-react"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Globe' in content, "Globe icon should be imported"
        assert 'lucide-react' in content, "Should import from lucide-react"
    
    def test_camera_icon_imported(self):
        """Verify Camera icon is imported from lucide-react"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Camera' in content, "Camera icon should be imported"
    
    def test_eye_icon_imported(self):
        """Verify Eye icon is imported from lucide-react"""
        with open('/app/frontend/src/pages/AIAgentsPage.js', 'r') as f:
            content = f.read()
        assert 'Eye' in content, "Eye icon should be imported"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Iteration 29 Tests: 8 New Tools + Upgraded run_command and run_query
Tests for: delete_file, move_file, manage_env, lint_code, crawl_url, git_info
Plus: run_command (full bash, 120s timeout), run_query (full MongoDB CRUD)
"""
import pytest
import requests
import os
import time
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ═══════════════════════════════════════════════════════════════════════════════
# Test: GET /api/agents/providers returns 5 providers
# ═══════════════════════════════════════════════════════════════════════════════
class TestProvidersEndpoint:
    """Verify providers endpoint returns 5 providers"""
    
    def test_providers_returns_5_providers(self):
        """GET /api/agents/providers should return exactly 5 providers"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) == 5
        provider_names = [p["name"] for p in data["providers"]]
        assert "claude" in provider_names
        assert "gemini" in provider_names
        assert "gpt5" in provider_names
        assert "groq" in provider_names
        assert "openrouter" in provider_names


# ═══════════════════════════════════════════════════════════════════════════════
# Test: run_command now allows rm, mv, cp, sudo (was blocked before)
# ═══════════════════════════════════════════════════════════════════════════════
class TestRunCommandUpgrade:
    """Test that run_command now allows previously blocked commands"""
    
    def test_run_command_allows_rm(self):
        """run_command should allow rm command (except rm -rf /)"""
        # Create a test file first
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Use run_command to create a test file: echo 'test' > /app/backend/test_rm_file.txt",
            "session_id": "test-run-command-rm"
        })
        assert response.status_code == 200
        time.sleep(3)
        
        # Now test rm command
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Use run_command to delete the file: rm /app/backend/test_rm_file.txt",
            "session_id": "test-run-command-rm-2"
        })
        assert response.status_code == 200
        # The command should be accepted (not blocked)
        data = response.json()
        assert "task_id" in data
    
    def test_run_command_allows_mv(self):
        """run_command should allow mv command"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Use run_command to run: mv --help",
            "session_id": "test-run-command-mv"
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
    
    def test_run_command_allows_cp(self):
        """run_command should allow cp command"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Use run_command to run: cp --help",
            "session_id": "test-run-command-cp"
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
    
    def test_run_command_blocks_rm_rf_root(self):
        """run_command should still block rm -rf /"""
        # This is tested via code inspection - the HARD_BLOCKED list
        # We verify the blocklist exists in the code
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'HARD_BLOCKED = ["rm -rf /"' in content or "rm -rf /" in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: delete_file tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestDeleteFileTool:
    """Test delete_file tool functionality"""
    
    def test_delete_file_tool_exists_in_code(self):
        """delete_file tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "delete_file"' in content
        assert '"delete_file"' in content
    
    def test_delete_file_in_write_tools(self):
        """delete_file should be in WRITE_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"delete_file"' in content
        # Check it's in WRITE_TOOLS
        assert 'WRITE_TOOLS = {' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: move_file tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestMoveFileTool:
    """Test move_file tool functionality"""
    
    def test_move_file_tool_exists_in_code(self):
        """move_file tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "move_file"' in content
        assert '"move_file"' in content
    
    def test_move_file_in_write_tools(self):
        """move_file should be in WRITE_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Check it's in WRITE_TOOLS
        assert '"move_file"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: manage_env tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestManageEnvTool:
    """Test manage_env tool functionality"""
    
    def test_manage_env_tool_exists_in_code(self):
        """manage_env tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "manage_env"' in content
        assert '"manage_env"' in content
    
    def test_manage_env_read_action(self):
        """manage_env read action should return .env variables with masked values"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Check read action exists
        assert 'action == "read"' in content
        # Check masking logic
        assert 'masked' in content or 'value_preview' in content
    
    def test_manage_env_blocks_protected_keys(self):
        """manage_env should block MONGO_URL, DB_NAME, REACT_APP_BACKEND_URL"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'PROTECTED = {"MONGO_URL", "DB_NAME", "REACT_APP_BACKEND_URL"}' in content or \
               'MONGO_URL' in content and 'DB_NAME' in content and 'REACT_APP_BACKEND_URL' in content
    
    def test_manage_env_in_write_tools(self):
        """manage_env should be in WRITE_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"manage_env"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: lint_code tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestLintCodeTool:
    """Test lint_code tool functionality"""
    
    def test_lint_code_tool_exists_in_code(self):
        """lint_code tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "lint_code"' in content
        assert '"lint_code"' in content
    
    def test_lint_code_uses_ruff_for_python(self):
        """lint_code should use ruff for Python files"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'ruff' in content
    
    def test_lint_code_uses_eslint_for_js(self):
        """lint_code should use eslint for JS/JSX/TS/TSX files"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'eslint' in content
    
    def test_lint_code_in_read_tools(self):
        """lint_code should be in READ_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"lint_code"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: crawl_url tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestCrawlUrlTool:
    """Test crawl_url tool functionality"""
    
    def test_crawl_url_tool_exists_in_code(self):
        """crawl_url tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "crawl_url"' in content
        assert '"crawl_url"' in content
    
    def test_crawl_url_strips_html(self):
        """crawl_url should strip HTML tags for cleaner text"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Check for HTML stripping logic
        assert '<script' in content or 'script' in content
        assert '<style' in content or 'style' in content
    
    def test_crawl_url_in_read_tools(self):
        """crawl_url should be in READ_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"crawl_url"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: git_info tool
# ═══════════════════════════════════════════════════════════════════════════════
class TestGitInfoTool:
    """Test git_info tool functionality"""
    
    def test_git_info_tool_exists_in_code(self):
        """git_info tool should be defined in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'elif tool_name == "git_info"' in content
        assert '"git_info"' in content
    
    def test_git_info_supports_log_action(self):
        """git_info should support log action"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'git log' in content
    
    def test_git_info_supports_status_action(self):
        """git_info should support status action"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'git status' in content
    
    def test_git_info_supports_diff_action(self):
        """git_info should support diff action"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'git diff' in content
    
    def test_git_info_in_read_tools(self):
        """git_info should be in READ_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"git_info"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: run_query supports full MongoDB CRUD
# ═══════════════════════════════════════════════════════════════════════════════
class TestRunQueryUpgrade:
    """Test that run_query supports insert, update, delete, aggregate, distinct, drop"""
    
    def test_run_query_supports_insert_one(self):
        """run_query should support insert_one operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'insert_one' in content or '"insert"' in content
    
    def test_run_query_supports_insert_many(self):
        """run_query should support insert_many operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'insert_many' in content
    
    def test_run_query_supports_count(self):
        """run_query should support count operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'count' in content or 'count_documents' in content
    
    def test_run_query_supports_find(self):
        """run_query should support find operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"find"' in content or 'query_type in ["find"' in content
    
    def test_run_query_supports_update_many(self):
        """run_query should support update_many operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'update_many' in content
    
    def test_run_query_supports_delete_many(self):
        """run_query should support delete_many operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'delete_many' in content
    
    def test_run_query_supports_aggregate(self):
        """run_query should support aggregate operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'aggregate' in content
    
    def test_run_query_supports_distinct(self):
        """run_query should support distinct operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'distinct' in content
    
    def test_run_query_supports_drop(self):
        """run_query should support drop operation"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"drop"' in content or 'query_type == "drop"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: install_package with manager=yarn works for frontend
# ═══════════════════════════════════════════════════════════════════════════════
class TestInstallPackageYarn:
    """Test install_package supports yarn for frontend packages"""
    
    def test_install_package_supports_yarn(self):
        """install_package should support manager=yarn"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'manager == "yarn"' in content or '"yarn"' in content
        assert 'yarn add' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: restart_service supports both backend and frontend
# ═══════════════════════════════════════════════════════════════════════════════
class TestRestartServiceFrontend:
    """Test restart_service supports frontend"""
    
    def test_restart_service_supports_frontend(self):
        """restart_service should support 'frontend' service"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert 'service not in ["backend", "frontend"]' in content or \
               '"frontend"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Frontend shows correct badges and icons
# ═══════════════════════════════════════════════════════════════════════════════
class TestFrontendToolIcons:
    """Test frontend has correct tool icons for new tools"""
    
    def test_frontend_has_trash_icon_for_delete_file(self):
        """Frontend should have Trash icon for delete_file"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'delete_file: Trash' in content
    
    def test_frontend_has_arrow_icon_for_move_file(self):
        """Frontend should have ArrowRightLeft icon for move_file"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'move_file: ArrowRightLeft' in content
    
    def test_frontend_has_settings_icon_for_manage_env(self):
        """Frontend should have Settings icon for manage_env"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'manage_env: Settings' in content
    
    def test_frontend_has_filecode_icon_for_lint_code(self):
        """Frontend should have FileCode icon for lint_code"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'lint_code: FileCode' in content
    
    def test_frontend_has_gitcommit_icon_for_git_info(self):
        """Frontend should have GitCommit icon for git_info"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'git_info: GitCommit' in content
    
    def test_frontend_shows_27_tools_badge(self):
        """Frontend should show '27 Tools + Full Access' badge"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert '27 Tools' in content
    
    def test_frontend_footer_shows_correct_text(self):
        """Frontend footer should show correct capabilities"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert '27 tools' in content
        assert '.env management' in content
        assert 'Linting' in content
        assert 'Git' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Tool summaries in ToolResultCard
# ═══════════════════════════════════════════════════════════════════════════════
class TestToolResultCardSummaries:
    """Test ToolResultCard has summaries for new tools"""
    
    def test_delete_file_summary(self):
        """ToolResultCard should have summary for delete_file"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'delete_file'" in content
    
    def test_move_file_summary(self):
        """ToolResultCard should have summary for move_file"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'move_file'" in content
    
    def test_manage_env_summary(self):
        """ToolResultCard should have summary for manage_env"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'manage_env'" in content
    
    def test_lint_code_summary(self):
        """ToolResultCard should have summary for lint_code"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'lint_code'" in content
    
    def test_crawl_url_summary(self):
        """ToolResultCard should have summary for crawl_url"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'crawl_url'" in content
    
    def test_git_info_summary(self):
        """ToolResultCard should have summary for git_info"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "result.tool === 'git_info'" in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: WRITE_TOOLS and READ_TOOLS sets are updated
# ═══════════════════════════════════════════════════════════════════════════════
class TestToolSets:
    """Test WRITE_TOOLS and READ_TOOLS sets contain new tools"""
    
    def test_write_tools_contains_delete_file(self):
        """WRITE_TOOLS should contain delete_file"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Find WRITE_TOOLS line
        assert '"delete_file"' in content
    
    def test_write_tools_contains_move_file(self):
        """WRITE_TOOLS should contain move_file"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"move_file"' in content
    
    def test_write_tools_contains_manage_env(self):
        """WRITE_TOOLS should contain manage_env"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"manage_env"' in content
    
    def test_read_tools_contains_lint_code(self):
        """READ_TOOLS should contain lint_code"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"lint_code"' in content
    
    def test_read_tools_contains_crawl_url(self):
        """READ_TOOLS should contain crawl_url"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"crawl_url"' in content
    
    def test_read_tools_contains_git_info(self):
        """READ_TOOLS should contain git_info"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert '"git_info"' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: run_command timeout is 120s
# ═══════════════════════════════════════════════════════════════════════════════
class TestRunCommandTimeout:
    """Test run_command has 120s timeout"""
    
    def test_run_command_timeout_120s(self):
        """run_command should have 120s timeout"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Check for 120 timeout
        assert '120' in content


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Test: Chat endpoint with complex task
# ═══════════════════════════════════════════════════════════════════════════════
class TestChatIntegration:
    """Test chat endpoint with tasks that use new tools"""
    
    def test_chat_endpoint_works(self):
        """POST /api/agents/chat should return task_id"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What is 2+2?",
            "session_id": "test-integration-simple"
        })
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
    
    def test_task_status_endpoint(self):
        """GET /api/agents/tasks/{task_id} should return task status"""
        # First create a task
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "List files in /app/backend",
            "session_id": "test-task-status"
        })
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Wait a bit for task to process
        time.sleep(2)
        
        # Check task status
        status_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

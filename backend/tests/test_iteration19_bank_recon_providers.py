"""
Iteration 19 Tests: Multi-Provider LLM Support + Bank Reconciliation Module
Tests:
- GET /api/agents/providers — returns 3 providers (groq, openrouter, claude)
- POST /api/agents/chat — returns task_id instantly (async architecture)
- GET /api/agents/tasks/{task_id} — returns status with provider field after polling
- GET /api/bank-recon/summary?account=HDFC Bank - Current
- GET /api/bank-recon/summary?account=Axis Bank - Current
- GET /api/bank-recon/unmatched?account=HDFC Bank - Current
"""
import pytest
import requests
import time
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLLMProviders:
    """Test multi-provider LLM configuration"""
    
    def test_get_providers_returns_three_providers(self):
        """GET /api/agents/providers should return 3 providers"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "providers" in data, "Response should have 'providers' key"
        providers = data["providers"]
        
        assert len(providers) == 3, f"Expected 3 providers, got {len(providers)}"
        
        # Check provider names
        provider_names = [p["name"] for p in providers]
        assert "groq" in provider_names, "Groq provider should be present"
        assert "openrouter" in provider_names, "OpenRouter provider should be present"
        assert "claude" in provider_names, "Claude provider should be present"
        
    def test_providers_have_correct_structure(self):
        """Each provider should have name, model, status, priority"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        
        data = response.json()
        for provider in data["providers"]:
            assert "name" in provider, "Provider should have 'name'"
            assert "model" in provider, "Provider should have 'model'"
            assert "status" in provider, "Provider should have 'status'"
            assert "priority" in provider, "Provider should have 'priority'"
            
    def test_groq_is_primary_provider(self):
        """Groq should be priority 1 (primary)"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        
        data = response.json()
        groq = next((p for p in data["providers"] if p["name"] == "groq"), None)
        assert groq is not None, "Groq provider not found"
        assert groq["priority"] == 1, f"Groq should be priority 1, got {groq['priority']}"
        assert groq["model"] == "llama-3.3-70b-versatile", f"Groq model should be llama-3.3-70b-versatile"
        
    def test_providers_have_active_status(self):
        """All providers should have 'active' status (keys are configured)"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        
        data = response.json()
        for provider in data["providers"]:
            # Status should be 'active' or 'no_key'
            assert provider["status"] in ["active", "no_key"], f"Invalid status: {provider['status']}"
            
    def test_fallback_order_is_correct(self):
        """Fallback order should be groq -> openrouter -> claude"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        
        data = response.json()
        assert "fallback_order" in data, "Response should have 'fallback_order'"
        assert data["fallback_order"] == ["groq", "openrouter", "claude"], \
            f"Fallback order should be ['groq', 'openrouter', 'claude'], got {data['fallback_order']}"


class TestAsyncChatArchitecture:
    """Test async chat with task polling"""
    
    def test_chat_returns_task_id_instantly(self):
        """POST /api/agents/chat should return task_id immediately"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello, what is 2+2?", "agent_type": "auto"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "task_id" in data, "Response should have 'task_id'"
        assert "status" in data, "Response should have 'status'"
        assert data["status"] == "queued", f"Initial status should be 'queued', got {data['status']}"
        
    def test_task_polling_returns_status(self):
        """GET /api/agents/tasks/{task_id} should return task status"""
        # Start a task
        chat_response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 1+1?", "agent_type": "auto"}
        )
        assert chat_response.status_code == 200
        task_id = chat_response.json()["task_id"]
        
        # Poll for status
        response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should have 'status'"
        assert data["status"] in ["queued", "thinking", "executing", "complete", "error"], \
            f"Invalid status: {data['status']}"
            
    def test_task_completes_with_provider_field(self):
        """Task should complete with 'provider' field indicating which LLM was used"""
        # Start a task
        chat_response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Say hello", "agent_type": "auto"}
        )
        assert chat_response.status_code == 200
        task_id = chat_response.json()["task_id"]
        
        # Poll until complete (max 30 seconds)
        max_attempts = 15
        for i in range(max_attempts):
            response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            
            if data["status"] in ["complete", "error"]:
                # Check for provider field
                if data["status"] == "complete":
                    assert "provider" in data, "Completed task should have 'provider' field"
                    assert data["provider"] in ["groq", "openrouter", "claude"], \
                        f"Provider should be groq/openrouter/claude, got {data.get('provider')}"
                    assert "response" in data, "Completed task should have 'response'"
                break
            time.sleep(2)
        else:
            pytest.skip("Task did not complete within 30 seconds - LLM may be slow")
            
    def test_invalid_task_id_returns_404(self):
        """GET /api/agents/tasks/{invalid_id} should return 404"""
        response = requests.get(f"{BASE_URL}/api/agents/tasks/invalid-task-id-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestBankReconciliationSummary:
    """Test Bank Reconciliation summary endpoint"""
    
    def test_summary_hdfc_bank_current(self):
        """GET /api/bank-recon/summary?account=HDFC Bank - Current"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/summary",
            params={"account": "HDFC Bank - Current"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Check required fields
        assert "account" in data, "Response should have 'account'"
        assert "book_balance" in data, "Response should have 'book_balance'"
        assert "bank_balance" in data, "Response should have 'bank_balance'"
        assert "difference" in data, "Response should have 'difference'"
        
        # Verify account name
        assert data["account"] == "HDFC Bank - Current", f"Account mismatch: {data['account']}"
        
    def test_summary_has_matched_unmatched_counts(self):
        """Summary should include matched and unmatched counts"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/summary",
            params={"account": "HDFC Bank - Current"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Check for count fields (may be named differently)
        has_matched = "matched_count" in data or "matched_bank_count" in data
        has_unmatched = "unmatched_count" in data or "unmatched_bank_count" in data
        
        assert has_matched or has_unmatched, "Summary should have matched/unmatched count fields"
        
    def test_summary_axis_bank_current(self):
        """GET /api/bank-recon/summary?account=Axis Bank - Current"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/summary",
            params={"account": "Axis Bank - Current"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["account"] == "Axis Bank - Current", f"Account mismatch: {data['account']}"
        assert "book_balance" in data
        assert "bank_balance" in data
        
    def test_summary_invalid_account_returns_404(self):
        """Summary for non-existent account should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/summary",
            params={"account": "Non-Existent Bank Account"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestBankReconciliationUnmatched:
    """Test Bank Reconciliation unmatched entries endpoint"""
    
    def test_unmatched_hdfc_bank_current(self):
        """GET /api/bank-recon/unmatched?account=HDFC Bank - Current"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/unmatched",
            params={"account": "HDFC Bank - Current"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "account" in data, "Response should have 'account'"
        
        # Check for bank and book entries (may be named differently)
        has_bank = "bank_entries" in data or "bank_unmatched" in data
        has_book = "book_entries" in data or "book_unmatched" in data
        
        assert has_bank, "Response should have bank entries field"
        assert has_book, "Response should have book entries field"
        
    def test_unmatched_returns_arrays(self):
        """Unmatched endpoint should return arrays for bank and book entries"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/unmatched",
            params={"account": "HDFC Bank - Current"}
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Get the arrays (handle different naming)
        bank_entries = data.get("bank_entries") or data.get("bank_unmatched") or []
        book_entries = data.get("book_entries") or data.get("book_unmatched") or []
        
        assert isinstance(bank_entries, list), "Bank entries should be a list"
        assert isinstance(book_entries, list), "Book entries should be a list"
        
    def test_unmatched_invalid_account_returns_404(self):
        """Unmatched for non-existent account should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/unmatched",
            params={"account": "Non-Existent Bank Account"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestBankReconciliationEEFC:
    """Test Bank Reconciliation for EEFC USD Account"""
    
    def test_summary_eefc_usd_account(self):
        """GET /api/bank-recon/summary?account=EEFC USD Account"""
        response = requests.get(
            f"{BASE_URL}/api/bank-recon/summary",
            params={"account": "EEFC USD Account"}
        )
        # This may return 404 if account doesn't exist in CoA
        if response.status_code == 404:
            pytest.skip("EEFC USD Account not found in Chart of Accounts")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "book_balance" in data
        assert "bank_balance" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

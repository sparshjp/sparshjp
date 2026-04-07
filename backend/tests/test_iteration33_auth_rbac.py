"""
Iteration 33: JWT Authentication & RBAC Testing
Tests for the new auth system with 9 roles and section-level access control.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Creator credentials from env
CREATOR_EMAIL = "kairoserp"
CREATOR_PASSWORD = "¢re@tor@AIengine"


class TestAuthLogin:
    """Test login endpoint functionality"""
    
    def test_login_creator_success(self):
        """POST /api/auth/login with creator credentials returns token and user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREATOR_EMAIL,
            "password": CREATOR_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify token exists
        assert "token" in data, "Response should contain token"
        assert isinstance(data["token"], str), "Token should be a string"
        assert len(data["token"]) > 0, "Token should not be empty"
        
        # Verify user data
        assert "user" in data, "Response should contain user"
        user = data["user"]
        assert user["email"] == CREATOR_EMAIL, f"Email should be {CREATOR_EMAIL}"
        assert user["role"] == "creator", "Role should be creator"
        assert "password_hash" not in user, "Password hash should not be exposed"
        print(f"✓ Login successful for creator: {user['name']}")
    
    def test_login_wrong_password(self):
        """POST /api/auth/login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREATOR_EMAIL,
            "password": "wrongpassword123"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Wrong password correctly returns 401")
    
    def test_login_missing_credentials(self):
        """POST /api/auth/login with missing credentials returns 400"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "",
            "password": ""
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Missing credentials correctly returns 400")
    
    def test_login_nonexistent_user(self):
        """POST /api/auth/login with nonexistent user returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "somepassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Nonexistent user correctly returns 401")


class TestAuthMe:
    """Test /auth/me endpoint"""
    
    @pytest.fixture
    def creator_token(self):
        """Get creator token for authenticated tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREATOR_EMAIL,
            "password": CREATOR_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get creator token")
    
    def test_me_with_valid_token(self, creator_token):
        """GET /api/auth/me with valid bearer token returns user data"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {creator_token}"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        user = response.json()
        assert user["email"] == CREATOR_EMAIL
        assert user["role"] == "creator"
        assert "password_hash" not in user
        print(f"✓ /auth/me returns user: {user['name']} ({user['role']})")
    
    def test_me_without_token(self):
        """GET /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /auth/me without token correctly returns 401")
    
    def test_me_with_invalid_token(self):
        """GET /api/auth/me with invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": "Bearer invalid_token_here"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /auth/me with invalid token correctly returns 401")


class TestAuthRegister:
    """Test user registration"""
    
    def test_register_new_user_viewer_role(self):
        """POST /api/auth/register creates new user with viewer role by default"""
        import uuid
        test_email = f"test_viewer_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test Viewer"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "token" in data
        assert data["user"]["email"] == test_email
        assert data["user"]["role"] == "viewer", "Default role should be viewer"
        print(f"✓ Registered new user with viewer role: {test_email}")
    
    def test_register_with_creator_role_forbidden(self):
        """POST /api/auth/register with role=creator returns 403"""
        import uuid
        test_email = f"test_creator_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test Creator",
            "role": "creator"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Self-registration as creator correctly forbidden (403)")
    
    def test_register_short_password(self):
        """POST /api/auth/register with short password returns 400"""
        import uuid
        test_email = f"test_short_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "12345",  # Less than 6 chars
            "name": "Test Short"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Short password correctly rejected (400)")


class TestAuthRoles:
    """Test roles endpoint"""
    
    def test_get_roles(self):
        """GET /api/auth/roles returns all 9 roles with section_access"""
        response = requests.get(f"{BASE_URL}/api/auth/roles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify roles
        assert "roles" in data
        roles = data["roles"]
        expected_roles = ["creator", "admin", "finance_manager", "project_manager", 
                         "hr_manager", "ap_clerk", "ar_clerk", "tax_compliance", "viewer"]
        for role in expected_roles:
            assert role in roles, f"Missing role: {role}"
        
        # Verify section_access
        assert "section_access" in data
        section_access = data["section_access"]
        assert "ai" in section_access
        assert section_access["ai"] == ["creator"], "Only creator should have AI access"
        
        print(f"✓ All 9 roles returned with section_access")


class TestUserManagement:
    """Test user CRUD operations (admin/creator only)"""
    
    @pytest.fixture
    def creator_token(self):
        """Get creator token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREATOR_EMAIL,
            "password": CREATOR_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get creator token")
    
    def test_list_users_with_creator_token(self, creator_token):
        """GET /api/auth/users with creator token returns user list"""
        response = requests.get(f"{BASE_URL}/api/auth/users", headers={
            "Authorization": f"Bearer {creator_token}"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1, "Should have at least creator user"
        
        # Verify creator exists in list
        creator_found = any(u["email"] == CREATOR_EMAIL for u in users)
        assert creator_found, "Creator should be in user list"
        print(f"✓ User list returned {len(users)} users")
    
    def test_list_users_without_token(self):
        """GET /api/auth/users without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/users")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ User list without token correctly returns 401")
    
    def test_create_user_with_admin_token(self, creator_token):
        """POST /api/auth/users creates user with specified role"""
        import uuid
        test_email = f"test_admin_created_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/users", 
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "email": test_email,
                "password": "testpass123",
                "name": "Admin Created User",
                "role": "finance_manager"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        user = response.json()
        assert user["email"] == test_email
        assert user["role"] == "finance_manager"
        print(f"✓ Created user with finance_manager role: {test_email}")
        
        # Return user id for cleanup/further tests
        return user["id"]
    
    def test_update_user_role(self, creator_token):
        """PUT /api/auth/users/{id} updates user role"""
        import uuid
        # First create a user
        test_email = f"test_update_{uuid.uuid4().hex[:8]}@test.com"
        create_resp = requests.post(f"{BASE_URL}/api/auth/users",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "email": test_email,
                "password": "testpass123",
                "name": "Update Test User",
                "role": "viewer"
            }
        )
        assert create_resp.status_code == 200
        user_id = create_resp.json()["id"]
        
        # Update role
        update_resp = requests.put(f"{BASE_URL}/api/auth/users/{user_id}",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={"role": "ap_clerk"}
        )
        assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}"
        updated = update_resp.json()
        assert updated["role"] == "ap_clerk"
        print(f"✓ Updated user role from viewer to ap_clerk")
    
    def test_delete_creator_forbidden(self, creator_token):
        """DELETE /api/auth/users/{id} for creator account returns 403"""
        # Get creator user id
        users_resp = requests.get(f"{BASE_URL}/api/auth/users",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        users = users_resp.json()
        creator_user = next((u for u in users if u["role"] == "creator"), None)
        assert creator_user, "Creator user should exist"
        
        # Try to delete creator
        delete_resp = requests.delete(f"{BASE_URL}/api/auth/users/{creator_user['id']}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        assert delete_resp.status_code == 403, f"Expected 403, got {delete_resp.status_code}"
        print("✓ Deleting creator account correctly forbidden (403)")


class TestAuthLogout:
    """Test logout functionality"""
    
    def test_logout_clears_cookies(self):
        """POST /api/auth/logout returns ok status"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Logout returns ok status")


class TestBruteForceProtection:
    """Test brute force protection (5 failed logins locks account)"""
    
    def test_brute_force_lockout(self):
        """5 failed logins should lock account temporarily"""
        import uuid
        # Use a unique email to avoid affecting other tests
        test_email = f"bruteforce_test_{uuid.uuid4().hex[:8]}@test.com"
        
        # First register the user
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "correctpassword123",
            "name": "Brute Force Test"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        
        # Attempt 5 failed logins
        for i in range(5):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": test_email,
                "password": "wrongpassword"
            })
            assert response.status_code == 401, f"Attempt {i+1}: Expected 401"
        
        # 6th attempt should be locked (429)
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "wrongpassword"
        })
        assert response.status_code == 429, f"Expected 429 (locked), got {response.status_code}"
        assert "locked" in response.json().get("detail", "").lower()
        print("✓ Account locked after 5 failed attempts (429)")


class TestRoleBasedAccess:
    """Test role-based access to protected endpoints"""
    
    @pytest.fixture
    def viewer_token(self):
        """Create and login as viewer user"""
        import uuid
        test_email = f"test_viewer_access_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register viewer
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Viewer Access Test"
        })
        if reg_resp.status_code == 200:
            return reg_resp.json()["token"]
        pytest.skip("Could not create viewer user")
    
    def test_viewer_cannot_access_user_management(self, viewer_token):
        """Viewer role cannot access /api/auth/users"""
        response = requests.get(f"{BASE_URL}/api/auth/users", headers={
            "Authorization": f"Bearer {viewer_token}"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Viewer correctly denied access to user management (403)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

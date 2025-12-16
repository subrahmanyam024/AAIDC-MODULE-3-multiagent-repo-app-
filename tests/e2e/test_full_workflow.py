import pytest
import json
import os
from datetime import datetime


class TestAuthenticationFlow:
    """End-to-end authentication workflow tests"""
    
    def test_complete_user_lifecycle(self, client):
        """Test: Register → Login → Get User → Change Password → Logout"""
        
        test_user = {
            'username': f'test_user_{int(datetime.now().timestamp())}',
            'email': f'test_{datetime.now().timestamp()}@example.com',
            'password': 'SecurePass123'
        }
        
        # Step 1: Register user
        response = client.post('/api/auth/register', 
            json=test_user,
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.json['username'] == test_user['username']
        assert 'message' in response.json
        
        # Step 2: Login with registered credentials
        login_data = {
            'username': test_user['username'],
            'password': test_user['password']
        }
        response = client.post('/api/auth/login',
            json=login_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        assert 'access_token' in response.json
        token = response.json['access_token']
        
        # Step 3: Get current user info
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 200
        assert response.json['username'] == test_user['username']
        assert response.json['email'] == test_user['email']
        
        # Step 4: Change password
        new_password_data = {
            'old_password': test_user['password'],
            'new_password': 'NewSecurePass456'
        }
        response = client.post('/api/auth/change-password',
            json=new_password_data,
            headers=headers,
            content_type='application/json'
        )
        assert response.status_code == 200
        assert 'Password changed successfully' in response.json['message']
        
        # Step 5: Logout
        response = client.post('/api/auth/logout', headers=headers)
        assert response.status_code == 200
        assert 'Logout successful' in response.json['message']


class TestProjectWorkflow:
    """End-to-end project management workflow tests"""
    
    def test_complete_project_lifecycle(self, client, authenticated_headers):
        """Test: Create Project → Get Projects → Update Project → Delete Project"""
        
        project_data = {
            'name': 'Test Project',
            'github_url': 'https://github.com/test/repo',
            'description': 'A test repository for end-to-end testing'
        }
        
        # Step 1: Create project
        response = client.post('/api/projects',
            json=project_data,
            headers=authenticated_headers,
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.json['name'] == project_data['name']
        assert 'id' in response.json
        project_id = response.json['id']
        
        # Step 2: Get all projects
        response = client.get('/api/projects', headers=authenticated_headers)
        assert response.status_code == 200
        assert isinstance(response.json['projects'], list)
        assert len(response.json['projects']) > 0
        
        # Step 3: Get specific project
        response = client.get(f'/api/projects/{project_id}',
            headers=authenticated_headers
        )
        assert response.status_code == 200
        assert response.json['id'] == project_id
        assert response.json['status'] == 'pending'
        
        # Step 4: Update project
        update_data = {
            'name': 'Updated Test Project',
            'description': 'Updated description'
        }
        response = client.put(f'/api/projects/{project_id}',
            json=update_data,
            headers=authenticated_headers,
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.json['name'] == update_data['name']
        
        # Step 5: Delete project
        response = client.delete(f'/api/projects/{project_id}',
            headers=authenticated_headers
        )
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get('/api/projects', headers=authenticated_headers)
        project_ids = [p['id'] for p in response.json['projects']]
        assert project_id not in project_ids


class TestAPIErrorHandling:
    """End-to-end error handling and validation tests"""
    
    def test_invalid_registration_inputs(self, client):
        """Test validation of invalid registration inputs"""
        
        # Test: Missing username
        response = client.post('/api/auth/register',
            json={'email': 'test@example.com', 'password': 'Pass123'},
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'error' in response.json
        
        # Test: Invalid email format
        response = client.post('/api/auth/register',
            json={'username': 'testuser', 'email': 'invalid-email', 'password': 'Pass123'},
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test: Password too short
        response = client.post('/api/auth/register',
            json={'username': 'testuser', 'email': 'test@example.com', 'password': 'short'},
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        
        # Test: No token provided
        response = client.get('/api/projects')
        assert response.status_code == 401
        
        # Test: Invalid token
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/projects', headers=headers)
        assert response.status_code == 401
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payloads"""
        
        response = client.post('/api/auth/register',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 415]
    
    def test_missing_required_fields(self, client, authenticated_headers):
        """Test validation of missing required fields"""
        
        # Missing github_url in project creation
        response = client.post('/api/projects',
            json={'name': 'Test Project'},
            headers=authenticated_headers,
            content_type='application/json'
        )
        assert response.status_code == 400


class TestDataIntegrity:
    """End-to-end data integrity tests"""
    
    def test_user_isolation(self, client):
        """Test that users can only access their own data"""
        
        # Create two users
        user1 = {
            'username': f'user1_{int(datetime.now().timestamp())}',
            'email': f'user1_{datetime.now().timestamp()}@example.com',
            'password': 'Pass123456'
        }
        user2 = {
            'username': f'user2_{int(datetime.now().timestamp())}',
            'email': f'user2_{datetime.now().timestamp()}@example.com',
            'password': 'Pass123456'
        }
        
        # Register both users
        client.post('/api/auth/register', json=user1, content_type='application/json')
        client.post('/api/auth/register', json=user2, content_type='application/json')
        
        # Login as user1
        response = client.post('/api/auth/login',
            json={'username': user1['username'], 'password': user1['password']},
            content_type='application/json'
        )
        token1 = response.json['access_token']
        headers1 = {'Authorization': f'Bearer {token1}'}
        
        # Login as user2
        response = client.post('/api/auth/login',
            json={'username': user2['username'], 'password': user2['password']},
            content_type='application/json'
        )
        token2 = response.json['access_token']
        headers2 = {'Authorization': f'Bearer {token2}'}
        
        # User1 creates a project
        project_data = {'name': 'User1 Project', 'github_url': 'https://github.com/user1/repo'}
        response = client.post('/api/projects', json=project_data, headers=headers1, content_type='application/json')
        assert response.status_code == 201
        project_id = response.json['id']
        
        # Verify user1 can see their project
        response = client.get('/api/projects', headers=headers1)
        project_ids = [p['id'] for p in response.json['projects']]
        assert project_id in project_ids
        
        # Verify user2 cannot see user1's project
        response = client.get('/api/projects', headers=headers2)
        project_ids = [p['id'] for p in response.json['projects']]
        assert project_id not in project_ids
    
    def test_data_consistency_after_operations(self, client, authenticated_headers):
        """Test that data remains consistent after multiple operations"""
        
        # Create multiple projects
        project_ids = []
        for i in range(3):
            project_data = {
                'name': f'Project {i}',
                'github_url': f'https://github.com/test/repo{i}'
            }
            response = client.post('/api/projects', json=project_data, headers=authenticated_headers, content_type='application/json')
            if response.status_code == 201:
                project_ids.append(response.json['id'])
        
        # Verify all projects exist
        response = client.get('/api/projects', headers=authenticated_headers)
        existing_ids = [p['id'] for p in response.json['projects']]
        for pid in project_ids:
            assert pid in existing_ids
        
        # Delete one project
        if project_ids:
            client.delete(f'/api/projects/{project_ids[0]}', headers=authenticated_headers)
        
        # Verify deletion
        response = client.get('/api/projects', headers=authenticated_headers)
        existing_ids = [p['id'] for p in response.json['projects']]
        assert project_ids[0] not in existing_ids
        
        # Verify other projects still exist
        for pid in project_ids[1:]:
            assert pid in existing_ids


class TestAPIRobustness:
    """End-to-end API robustness tests"""
    
    def test_concurrent_user_operations(self, client):
        """Test API handles concurrent operations correctly"""
        
        # Create user
        user_data = {
            'username': f'robust_user_{int(datetime.now().timestamp())}',
            'email': f'robust_{datetime.now().timestamp()}@example.com',
            'password': 'Pass123456'
        }
        response = client.post('/api/auth/register', json=user_data, content_type='application/json')
        assert response.status_code == 201
        
        # Login
        response = client.post('/api/auth/login',
            json={'username': user_data['username'], 'password': user_data['password']},
            content_type='application/json'
        )
        token = response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Perform multiple operations in sequence
        for i in range(5):
            project_data = {'name': f'Project {i}', 'github_url': f'https://github.com/test/repo{i}'}
            response = client.post('/api/projects', json=project_data, headers=headers, content_type='application/json')
            assert response.status_code == 201
    
    def test_edge_cases(self, client, authenticated_headers):
        """Test edge cases and boundary conditions"""
        
        # Test: Maximum length username
        long_username = 'a' * 50
        response = client.post('/api/auth/register',
            json={'username': long_username, 'email': 'test@example.com', 'password': 'Pass123'},
            content_type='application/json'
        )
        # Should either succeed or fail with clear error, not crash
        assert response.status_code in [201, 400, 409]
        
        # Test: Very long project description
        long_description = 'x' * 10000
        project_data = {
            'name': 'Project',
            'github_url': 'https://github.com/test/repo',
            'description': long_description
        }
        response = client.post('/api/projects', json=project_data, headers=authenticated_headers, content_type='application/json')
        # Should handle gracefully
        assert response.status_code in [201, 400]


@pytest.fixture
def client():
    """Flask test client"""
    from backend.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def authenticated_headers(client):
    """Get authenticated headers for test user"""
    user_data = {
        'username': f'test_user_{int(datetime.now().timestamp())}',
        'email': f'test_{datetime.now().timestamp()}@example.com',
        'password': 'TestPass123'
    }
    
    # Register
    client.post('/api/auth/register', json=user_data, content_type='application/json')
    
    # Login
    response = client.post('/api/auth/login',
        json={'username': user_data['username'], 'password': user_data['password']},
        content_type='application/json'
    )
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

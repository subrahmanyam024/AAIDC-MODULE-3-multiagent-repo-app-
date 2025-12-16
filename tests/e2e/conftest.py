import pytest
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))


@pytest.fixture(scope='function')
def client():
    """Flask test client for end-to-end tests"""
    from backend.app import app
    
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def test_user():
    """Fixture for test user data"""
    timestamp = int(datetime.now().timestamp() * 1000)
    return {
        'username': f'test_user_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'TestPass123456'
    }


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Flask test client with authenticated user"""
    
    # Register test user
    response = client.post('/api/auth/register',
        json=test_user,
        content_type='application/json'
    )
    assert response.status_code == 201
    
    # Login to get token
    response = client.post('/api/auth/login',
        json={
            'username': test_user['username'],
            'password': test_user['password']
        },
        content_type='application/json'
    )
    assert response.status_code == 200
    
    # Add token to client
    client.token = response.json['access_token']
    client.test_user = test_user
    
    return client


@pytest.fixture(scope='function')
def authenticated_headers(authenticated_client):
    """Get authenticated headers from client"""
    return {
        'Authorization': f'Bearer {authenticated_client.token}',
        'Content-Type': 'application/json'
    }

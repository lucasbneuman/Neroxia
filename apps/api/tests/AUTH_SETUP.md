# API Tests - Authentication Setup

## Problem

The API tests were failing because they tried to authenticate against Supabase, which:
1. Requires real user credentials
2. May not be available in test environment
3. Slows down test execution
4. Creates dependency on external service

## Solution

Implemented **mock authentication** using FastAPI's dependency override system.

### How It Works

1. **Mock Token**: Tests use a fake token `"mock_test_token_for_api_tests"`
2. **Dependency Override**: The `get_current_user` dependency is mocked to return a test user
3. **No Real Auth**: Tests bypass Supabase completely

### Implementation

In `conftest.py`:

```python
@pytest.fixture(autouse=True)
def mock_auth_dependency(monkeypatch):
    """Mock authentication for all tests."""
    from src.routers.auth import get_current_user
    
    async def mock_get_current_user():
        return {
            "id": "test-user-id-123",
            "email": "test@example.com",
            "user_metadata": {"name": "Test User"},
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()
```

### Benefits

✅ Tests run without Supabase
✅ Faster test execution
✅ No need for test credentials
✅ Tests are isolated and repeatable
✅ Works in CI/CD environments

### Running Tests

```powershell
cd apps\api
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Future Improvements

- Add integration tests with real Supabase (optional)
- Test different user roles/permissions
- Test token expiration scenarios

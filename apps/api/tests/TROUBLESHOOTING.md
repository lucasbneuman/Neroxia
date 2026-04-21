# Test Troubleshooting Guide

**Purpose**: Quick reference for common test issues and solutions  
**Last Updated**: 2025-11-24  
**Maintained by**: QA Agent

---

## 🚨 Common Issues

### 1. ImportError: email-validator is not installed

**Error**:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

**Solution**:
```bash
pip install pydantic[email]
```

**Why**: Auth API uses `EmailStr` type which requires email-validator package.

---

### 2. AttributeError: 'coroutine' object has no attribute 'id'

**Error**:
```
AttributeError: 'coroutine' object has no attribute 'id'
File "src\\routers\\bot.py", line 93, in process_bot_message
    messages_data = await crud.get_user_messages(db, user.id, limit=20)
```

**Status**: 🔴 Known Bug (#12) - Dev is fixing

**Workaround**: Skip integration tests until fixed
```bash
pytest tests/unit/ -v  # Run only unit tests
```

**Affected Tests**: 7 integration tests in `test_user_flows.py`

---

### 3. Tests Not Collected (0 tests found)

**Symptoms**:
- Pytest shows "collected 0 items"
- New test files not running

**Solutions**:

**A. Wrong Directory**:
```bash
# ❌ Wrong
cd neroxia
pytest tests/

# ✅ Correct
cd apps/api
pytest tests/
```

**B. Import Errors**:
```bash
# Check for import errors
pytest tests/ --collect-only
```

**C. File Naming**:
- Test files must start with `test_`
- Test functions must start with `test_`
- Test classes must start with `Test`

---

### 4. 401 Unauthorized Errors

**Error**:
```
assert 401 == 200
AssertionError: Should require authentication
```

**Cause**: Bug #11 - Mock auth too permissive

**Status**: 🟡 Known issue - affects 11 tests

**Explanation**: Mock authentication applies globally, making all endpoints appear authenticated even without headers.

**Affected Tests**:
- `test_*_requires_auth` tests
- Any test checking for 401 responses

---

### 5. 500 Internal Server Error in Tests

**Common Causes**:

**A. Database Connection Issues**:
```bash
# Check if database is accessible
python scripts/tests/test_db_connection.py
```

**B. Missing Environment Variables**:
```bash
# Check .env file exists
ls .env

# Verify Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

**C. Async Mock Issues** (Bug #12):
- See issue #2 above

---

### 6. Tests Timeout

**Error**:
```
FAILED tests/test_bot_api.py::test_process_message - TimeoutError
```

**Solutions**:

**A. Increase Timeout**:
```python
# In conftest.py or test file
@pytest.mark.timeout(30)  # 30 seconds
def test_slow_operation():
    pass
```

**B. Check External Services**:
- Verify API server is running
- Check database connection
- Verify Supabase is accessible

**C. Use Mocks**:
- Mock slow external services
- Use test fixtures instead of real data

---

### 7. Fixture Not Found

**Error**:
```
fixture 'auth_headers' not found
```

**Solution**:

**A. Check conftest.py Location**:
```
apps/api/tests/conftest.py  # Should exist here
```

**B. Verify Fixture Name**:
```python
# Available fixtures in conftest.py:
- client
- auth_token
- auth_headers
- test_phone
- test_config
- test_message
- db_session
- clean_db
```

**C. Check Scope**:
```python
# Some fixtures are session-scoped
@pytest.fixture(scope="session")
def auth_token():
    pass
```

---

### 8. Coverage Report Not Generated

**Error**:
```
Coverage.py warning: No data was collected
```

**Solutions**:

**A. Install pytest-cov**:
```bash
pip install pytest-cov
```

**B. Specify Source**:
```bash
pytest tests/ --cov=src --cov-report=html
```

**C. Check pytest.ini**:
```ini
[pytest]
addopts = --cov=src --cov-report=html
```

---

### 9. Parallel Execution Fails

**Error**:
```
ERROR: unknown option: -n
```

**Solution**:
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

**Note**: Some tests may fail in parallel due to shared state. Run sequentially if issues occur.

---

### 10. Mock Database Issues

**Symptoms**:
- Database validation tests fail
- Cannot access test database

**Solutions**:

**A. Check Mock Configuration**:
```python
# In conftest.py
@pytest.fixture
async def mock_get_db():
    # Verify this fixture exists and is correct
    pass
```

**B. Use Real DB for Integration Tests**:
```python
# Skip mock for specific tests
@pytest.mark.skip(reason="Requires real database")
def test_with_real_db():
    pass
```

---

## 🔍 Debugging Tips

### 1. Verbose Output
```bash
pytest tests/ -v -s  # Show print statements
```

### 2. Stop on First Failure
```bash
pytest tests/ -x  # Stop after first failure
pytest tests/ --maxfail=3  # Stop after 3 failures
```

### 3. Run Specific Test
```bash
pytest tests/unit/test_config_api.py::test_get_config_success -v
```

### 4. Show Locals on Failure
```bash
pytest tests/ -l  # Show local variables
```

### 5. Debug with PDB
```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

### 6. Collect Only (Don't Run)
```bash
pytest tests/ --collect-only  # See what tests would run
```

---

## 📝 Quick Commands Reference

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run in parallel
pytest tests/ -n auto

# Run specific file
pytest tests/unit/test_config_api.py -v

# Run specific test
pytest tests/unit/test_config_api.py::test_get_config_success -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -v -s

# Debug on failure
pytest tests/ --pdb
```

---

## 🐛 Known Bugs

### Active Bugs

| Bug # | Description | Status | Workaround |
|-------|-------------|--------|------------|
| #12 | Async mock returns coroutine | 🔴 Dev fixing | Skip integration tests |
| #11 | Mock auth too permissive | 🟡 Known | Expect some auth tests to fail |
| #10 | No DB validation | 🟡 Partial | DB fixtures created, pending implementation |

### Resolved Bugs

| Bug # | Description | Status | Fixed Date |
|-------|-------------|--------|------------|
| #9 | Missing API tests | ✅ Resolved | 2025-11-24 |
| email-validator | Missing dependency | ✅ Resolved | 2025-11-24 |

---

## 📞 Getting Help

1. **Check this guide first**
2. **Review test README**: `apps/api/tests/README.md`
3. **Check TASK_LOG**: `.agents/TASK_LOG.md` for recent changes
4. **Check BUG_TRACKER**: `.agents/BUG_TRACKER.md` for known issues
5. **Consult QA Agent** for test-related questions

---

## 🔄 Reporting New Issues

If you encounter a new issue:

1. **Document the error**:
   - Full error message
   - Steps to reproduce
   - Expected vs actual behavior

2. **Check if it's known**:
   - Review this guide
   - Check BUG_TRACKER.md

3. **Report to QA Agent**:
   - Include all details
   - Provide test output
   - Mention environment (OS, Python version)

---

**Last Updated**: 2025-11-24  
**Maintained by**: QA Agent  
**Version**: 1.0

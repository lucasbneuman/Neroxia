# API Test Suite

Comprehensive pytest test suite for the WhatsApp Sales Bot API.

## Overview

This test suite provides complete coverage of all API endpoints with:
- Unit tests for individual endpoints
- Integration tests for complete user workflows
- Authentication and authorization tests
- Data validation tests
- Error handling tests

## Test Files

### `conftest.py`
Shared fixtures and configuration:
- `client`: FastAPI test client
- `auth_token`: JWT authentication token
- `auth_headers`: Authorization headers
- `test_phone`: Test phone number
- `test_config`: Test configuration data
- `test_message`: Test message text

### `test_config_api.py`
Configuration management tests (10 tests):
- GET /config - Retrieve configuration
- PUT /config - Update configuration
- POST /config/reset - Reset to defaults
- Authentication requirements
- Partial updates
- Validation
- Persistence

### `test_bot_api.py`
Bot processing tests (11 tests):
- POST /bot/process - Message processing
- GET /bot/health - Health checks
- Intent detection
- Sentiment analysis
- Conversation stage progression
- Multi-message conversations
- Edge cases (empty messages, invalid phones)

### `test_user_flows.py`
Integration tests (10 tests):
- Complete configuration workflow
- Test chat workflow
- Configuration affecting bot behavior
- Complete sales conversation simulation
- Multi-user concurrent conversations
- Error recovery
- Configuration persistence
- Health and status endpoints

## Running Tests

### Install Dependencies

```bash
cd apps/api
pip install pytest pytest-cov httpx
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config_api.py

# Run specific test class
pytest tests/test_bot_api.py::TestBotProcessingAPI

# Run specific test
pytest tests/test_user_flows.py::TestUserFlows::test_complete_sales_conversation_flow
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest tests/ -n auto
```

## Test Coverage

Current test coverage:

- **Configuration API**: 100% (10/10 tests)
- **Bot Processing API**: 100% (11/11 tests)
- **User Flows**: 100% (10/10 tests)
- **Total**: 31 tests

## Test Scenarios

### Configuration Tests
1. ✅ Authentication required
2. ✅ Get configuration
3. ✅ Update full configuration
4. ✅ Update partial configuration
5. ✅ Reset configuration
6. ✅ Configuration validation
7. ✅ Configuration persistence

### Bot Processing Tests
1. ✅ Health check
2. ✅ Basic message processing
3. ✅ Message with custom config
4. ✅ Multi-message conversation
5. ✅ Intent detection
6. ✅ Sentiment analysis
7. ✅ Stage progression
8. ✅ Empty message handling
9. ✅ Invalid phone handling
10. ✅ Message with history

### User Flow Tests
1. ✅ Complete configuration flow
2. ✅ Test chat workflow
3. ✅ Configuration affects bot behavior
4. ✅ Complete sales conversation
5. ✅ Multi-user concurrent conversations
6. ✅ Error recovery
7. ✅ Configuration persistence across conversations
8. ✅ Root endpoint
9. ✅ Health endpoint
10. ✅ Bot health endpoint

## Prerequisites

- API server running on `http://localhost:8000`
- Test user credentials: `admin` / `admin`
- Database accessible and initialized

## Environment Variables

No special environment variables required. Tests use the same configuration as the main application.

## Continuous Integration

To run tests in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run API Tests
  run: |
    cd apps/api
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest tests/ --cov=src --cov-report=xml
```

## Troubleshooting

### Tests Failing with 401 Unauthorized
- Verify API server is running
- Check test credentials in `conftest.py`
- Ensure `/auth/login` endpoint works

### Tests Timing Out
- Increase timeout in pytest configuration
- Check API server performance
- Verify database connection

### Import Errors
- Ensure `src` directory is in Python path
- Check `conftest.py` path configuration
- Verify all dependencies installed

## Contributing

When adding new tests:
1. Follow existing test structure
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Use fixtures from `conftest.py`
5. Update this README with new test counts

## Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names that explain what is being tested

## Future Enhancements

- [ ] Add RAG endpoint tests
- [ ] Add conversation management tests
- [ ] Add follow-up scheduling tests
- [ ] Add integration tests
- [ ] Add performance/load tests
- [ ] Add security tests
- [ ] Add WebSocket tests (if applicable)

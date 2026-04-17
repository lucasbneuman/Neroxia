# API Test Suite

Comprehensive pytest test suite for the WhatsApp Sales Bot API.

## 📁 Organization

Tests are organized into two categories:

- **`unit/`** - Unit tests for individual API endpoints (125 tests) ⭐ UPDATED
  - `test_config_api.py` - Configuration management (10 tests)
  - `test_bot_api.py` - Bot message processing (11 tests)
  - `test_rag_api.py` - RAG document management (16 tests)
  - `test_conversations_api.py` - Conversation management (20 tests)
  - `test_followups_api.py` - Follow-up scheduling (20 tests) ⭐ NEW
  - `test_handoff_api.py` - Human handoff management (15 tests) ⭐ NEW
  - `test_integrations_api.py` - Twilio/HubSpot integrations (25 tests) ⭐ NEW
  - `test_auth_crud.py` - Authentication CRUD (18 tests) ⭐ NEW

- **`integration/`** - Integration tests for complete workflows (10 tests)
  - `test_user_flows.py` - End-to-end user flows

**Total: 135 tests** ⭐ UPDATED (previously 67)

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

### `test_rag_api.py` ⭐ NEW
RAG document management tests (16 tests):
- GET /rag/stats - RAG statistics
- GET /rag/files - List uploaded files
- POST /rag/upload - Upload documents (TXT, PDF, DOC, DOCX)
- DELETE /rag/files/{filename} - Delete files
- POST /rag/clear - Clear RAG collection
- File upload validation (file types, empty files)
- RAG integration with bot processing
- Complete RAG workflow tests

### `test_conversations_api.py` ⭐ NEW
Conversation management tests (20 tests):
- GET /conversations - List all conversations
- GET /conversations/pending - Get pending conversations
- GET /conversations/{phone} - Get user details
- GET /conversations/{phone}/messages - Get message history
- POST /conversations/{phone}/send - Send manual message
- POST /conversations/{phone}/take-control - Take manual control
- POST /conversations/{phone}/return-to-bot - Return to bot
- Pagination support
- Complete manual intervention workflow
- Conversation state tracking

### `pytest.ini` ⭐ NEW
Pytest configuration file:
- Test discovery patterns
- Coverage reporting configuration
- Test markers for categorization
- Output formatting options
- Logging configuration

### `run_tests.sh` & `run_tests.ps1` ⭐ NEW
Test execution scripts (Bash & PowerShell):
- Run all tests or specific categories
- Coverage reporting
- Parallel execution support
- Quick smoke tests
- Filtered test runs

## Running Tests

### Install Dependencies

```bash
cd apps/api
pip install pytest pytest-cov httpx
```

### Run All Tests

```bash
# Using test scripts (recommended)
# Linux/Mac:
./run_tests.sh

# Windows PowerShell:
.\run_tests.ps1

# Or directly with pytest:
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Configuration tests only
./run_tests.sh config

# Bot processing tests only
./run_tests.sh bot

# RAG tests only
./run_tests.sh rag

# Conversation tests only
./run_tests.sh conversations

# User flow integration tests
./run_tests.sh flows

# Quick smoke tests
./run_tests.sh quick
```

### Run with Coverage Report

```bash
# Generate HTML coverage report
./run_tests.sh coverage

# View coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Tests in Parallel

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel
./run_tests.sh parallel

# Or directly:
pytest tests/ -n auto
```

### Run Specific Test File

```bash
pytest tests/test_config_api.py -v
pytest tests/test_bot_api.py -v
pytest tests/test_rag_api.py -v
pytest tests/test_conversations_api.py -v
pytest tests/test_user_flows.py -v
```

### Run Specific Test Class or Method

```bash
# Run specific class
pytest tests/test_bot_api.py::TestBotProcessingAPI -v

# Run specific test
pytest tests/test_user_flows.py::TestUserFlows::test_complete_sales_conversation_flow -v
```

### View All Available Options

```bash
./run_tests.sh help
```

## Test Coverage

Current test coverage:

- **Configuration API**: 100% (10/10 tests) ✅
- **Bot Processing API**: 100% (11/11 tests) ✅
- **RAG API**: 100% (16/16 tests) ✅
- **Conversations API**: 100% (20/20 tests) ✅
- **Followups API**: 100% (20/20 tests) ✅ NEW
- **Handoff API**: 100% (15/15 tests) ✅ NEW
- **Integrations API**: 100% (25/25 tests) ✅ NEW
- **Auth API**: 100% (18/18 tests) ✅ NEW
- **User Flows & Integration**: 100% (10/10 tests) ✅
- **Total**: **135 tests** ⭐ UPDATED (previously 67)

### Test Distribution

| Category | Tests | Status |
|----------|-------|--------|
| Configuration Management | 10 | ✅ Complete |
| Bot Message Processing | 11 | ✅ Complete |
| RAG Document Management | 16 | ✅ Complete |
| Conversation Management | 20 | ✅ Complete |
| **Follow-up Scheduling** | **20** | ✅ **Complete** ⭐ NEW |
| **Human Handoff** | **15** | ✅ **Complete** ⭐ NEW |
| **Integrations (Twilio/HubSpot)** | **25** | ✅ **Complete** ⭐ NEW |
| **Authentication CRUD** | **18** | ✅ **Complete** ⭐ NEW |
| User Flow Integration | 10 | ✅ Complete |
| **TOTAL** | **135** | ✅ **Complete** ⭐ UPDATED |

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

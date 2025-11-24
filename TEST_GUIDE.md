# WhatsApp Sales Bot - Test Guide

Complete guide for running and maintaining tests across the project.

## 📁 Test Organization

The project uses a microservices architecture with tests organized by service:

```
whatsapp_sales_bot/
├── apps/
│   ├── api/tests/              # API Tests (67 tests)
│   │   ├── unit/               # Unit tests for API endpoints
│   │   │   ├── test_config_api.py (10 tests)
│   │   │   ├── test_bot_api.py (11 tests)
│   │   │   ├── test_rag_api.py (16 tests)
│   │   │   └── test_conversations_api.py (20 tests)
│   │   ├── integration/        # Integration tests
│   │   │   └── test_user_flows.py (10 tests)
│   │   ├── conftest.py
│   │   ├── pytest.ini
│   │   └── README.md
│   │
│   └── bot-engine/tests/       # Bot Engine Tests (LLM Agent)
│       ├── unit/               # Unit tests for bot components
│       │   ├── test_llm_service.py
│       │   ├── test_message_formatting.py
│       │   └── test_nodes.py
│       ├── integration/        # Integration tests
│       │   ├── test_llm_optimizations.py
│       │   └── test_sprint2_features.py
│       ├── conftest.py
│       ├── pytest.ini
│       └── README.md
│
└── scripts/
    ├── tests/                  # Utility test scripts
    │   ├── test_db_connection.py
    │   ├── test_db_only.py
    │   ├── test_integration.py
    │   ├── test_supabase.py
    │   └── test_supabase_simple.py
    └── utils/                  # Utility scripts
        └── create_test_user.py
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install pytest pytest-cov httpx

# For parallel execution
pip install pytest-xdist
```

### Running Tests

#### All Tests

```bash
# Run all API tests
cd apps/api && pytest tests/ -v

# Run all bot-engine tests
cd apps/bot-engine && pytest tests/ -v
```

#### By Category

```bash
# API unit tests only
cd apps/api && pytest tests/unit/ -v

# API integration tests only
cd apps/api && pytest tests/integration/ -v

# Bot-engine unit tests
cd apps/bot-engine && pytest tests/unit/ -v

# Bot-engine integration tests
cd apps/bot-engine && pytest tests/integration/ -v
```

#### Using Test Scripts

```bash
# API tests (Linux/Mac)
cd apps/api && ./run_tests.sh

# API tests (Windows)
cd apps/api && .\run_tests.ps1

# Specific categories
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh coverage
```

## 📊 Test Coverage

### API Tests (67 total)

| Category | Tests | Description |
|----------|-------|-------------|
| Configuration | 10 | GET/PUT config, reset, validation |
| Bot Processing | 11 | Message processing, health checks |
| RAG | 16 | Document upload, management |
| Conversations | 20 | List, details, manual control |
| User Flows | 10 | Complete workflows |

### Bot Engine Tests (LLM Agent)

| Category | Tests | Description |
|----------|-------|-------------|
| LLM Service | Multiple | LLM integration and optimization |
| Message Formatting | Multiple | Message formatting logic |
| Graph Nodes | Multiple | Bot graph node testing |
| Sprint 2 Features | Multiple | New feature testing |

## 🎯 Test Markers

Tests are categorized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run LLM-related tests
pytest -m llm

# Run slow tests
pytest -m slow
```

## 📝 Writing New Tests

### API Tests

Place in `apps/api/tests/`:
- **Unit tests** → `unit/test_*.py`
- **Integration tests** → `integration/test_*.py`

Example:
```python
# apps/api/tests/unit/test_my_feature.py
import pytest
from fastapi.testclient import TestClient

def test_my_feature(client: TestClient, auth_headers):
    response = client.get("/my-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

### Bot Engine Tests

Place in `apps/bot-engine/tests/`:
- **Unit tests** → `unit/test_*.py`
- **Integration tests** → `integration/test_*.py`

Example:
```python
# apps/bot-engine/tests/unit/test_my_component.py
import pytest

def test_my_component(sample_config):
    # Your test here
    pass
```

## 🔧 Utility Scripts

Located in `scripts/`:

- **tests/** - Test scripts for database, Supabase, integration
- **utils/** - Utility scripts like `create_test_user.py`

Run utility tests:
```bash
cd scripts/tests
python test_db_connection.py
python test_supabase.py
```

## 📚 Additional Resources

- [API Tests README](apps/api/tests/README.md) - Detailed API test documentation
- [Bot Engine Tests README](apps/bot-engine/tests/README.md) - Bot engine test documentation
- [pytest.ini](apps/api/pytest.ini) - API test configuration
- [pytest.ini](apps/bot-engine/pytest.ini) - Bot engine test configuration

## 🤝 Agent Collaboration

Tests are maintained by multiple agents:

- **QA Agent**: API tests, test organization, coverage
- **LLM Agent**: Bot engine tests, LLM optimizations
- **Dev Agent**: Bug fixes, feature tests

All test changes should be documented in `.agents/TASK_LOG.md` following the agent protocol.

## 💡 Tips

1. **Run tests before committing**: `pytest tests/ -v`
2. **Check coverage**: `pytest tests/ --cov=src --cov-report=html`
3. **Use markers**: Tag tests with `@pytest.mark.unit` or `@pytest.mark.integration`
4. **Keep tests fast**: Mock external services, use fixtures
5. **Document changes**: Update TASK_LOG.md when modifying tests

## 🐛 Troubleshooting

### Tests failing with import errors
```bash
# Ensure you're in the correct directory
cd apps/api  # or apps/bot-engine
pytest tests/
```

### Tests failing with auth errors
```bash
# Check test credentials in conftest.py
# Default: admin/admin
```

### Coverage not working
```bash
# Install coverage dependencies
pip install pytest-cov
```

## 📞 Support

For test-related questions:
1. Check this guide
2. Review test README in specific directory
3. Check `.agents/TASK_LOG.md` for recent changes
4. Consult with QA Agent or LLM Agent

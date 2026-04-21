#!/bin/bash
# Test execution script for Neroxia API
# Usage: ./run_tests.sh [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Neroxia API Test Suite ===${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov httpx"
    exit 1
fi

# Parse command line arguments
RUN_TYPE=${1:-all}

case $RUN_TYPE in
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ -v
        ;;
    
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        pytest tests/ -v -m unit
        ;;
    
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        pytest tests/ -v -m integration
        ;;
    
    smoke)
        echo -e "${YELLOW}Running smoke tests...${NC}"
        pytest tests/ -v -m smoke
        ;;
    
    coverage)
        echo -e "${YELLOW}Running tests with coverage report...${NC}"
        pytest tests/ -v --cov=src --cov-report=html --cov-report=term
        echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    config)
        echo -e "${YELLOW}Running configuration tests...${NC}"
        pytest tests/test_config_api.py -v
        ;;
    
    bot)
        echo -e "${YELLOW}Running bot processing tests...${NC}"
        pytest tests/test_bot_api.py -v
        ;;
    
    rag)
        echo -e "${YELLOW}Running RAG tests...${NC}"
        pytest tests/test_rag_api.py -v
        ;;
    
    conversations)
        echo -e "${YELLOW}Running conversation tests...${NC}"
        pytest tests/test_conversations_api.py -v
        ;;
    
    flows)
        echo -e "${YELLOW}Running user flow tests...${NC}"
        pytest tests/test_user_flows.py -v
        ;;
    
    parallel)
        echo -e "${YELLOW}Running tests in parallel...${NC}"
        if ! command -v pytest-xdist &> /dev/null; then
            echo -e "${RED}Error: pytest-xdist is not installed${NC}"
            echo "Install with: pip install pytest-xdist"
            exit 1
        fi
        pytest tests/ -v -n auto
        ;;
    
    quick)
        echo -e "${YELLOW}Running quick smoke tests...${NC}"
        pytest tests/ -v -k "health or root" --tb=short
        ;;
    
    help)
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run only unit tests"
        echo "  integration  - Run only integration tests"
        echo "  smoke        - Run smoke tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  config       - Run configuration API tests"
        echo "  bot          - Run bot processing tests"
        echo "  rag          - Run RAG API tests"
        echo "  conversations - Run conversation management tests"
        echo "  flows        - Run user flow tests"
        echo "  parallel     - Run tests in parallel (requires pytest-xdist)"
        echo "  quick        - Run quick smoke tests"
        echo "  help         - Show this help message"
        ;;
    
    *)
        echo -e "${RED}Error: Unknown option '$RUN_TYPE'${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Tests completed successfully${NC}"
else
    echo -e "\n${RED}✗ Tests failed${NC}"
    exit 1
fi

# Test execution script for Neroxia API (Windows PowerShell)
# Usage: .\run_tests.ps1 [options]

param(
    [string]$RunType = "all"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Neroxia API Test Suite ===" -ForegroundColor Green
Write-Host ""

# Check if pytest is installed
try {
    $null = Get-Command pytest -ErrorAction Stop
} catch {
    Write-Host "Error: pytest is not installed" -ForegroundColor Red
    Write-Host "Install with: pip install pytest pytest-cov httpx"
    exit 1
}

switch ($RunType) {
    "all" {
        Write-Host "Running all tests..." -ForegroundColor Yellow
        pytest tests/ -v
    }
    
    "unit" {
        Write-Host "Running unit tests..." -ForegroundColor Yellow
        pytest tests/ -v -m unit
    }
    
    "integration" {
        Write-Host "Running integration tests..." -ForegroundColor Yellow
        pytest tests/ -v -m integration
    }
    
    "smoke" {
        Write-Host "Running smoke tests..." -ForegroundColor Yellow
        pytest tests/ -v -m smoke
    }
    
    "coverage" {
        Write-Host "Running tests with coverage report..." -ForegroundColor Yellow
        pytest tests/ -v --cov=src --cov-report=html --cov-report=term
        Write-Host ""
        Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Green
    }
    
    "config" {
        Write-Host "Running configuration tests..." -ForegroundColor Yellow
        pytest tests/test_config_api.py -v
    }
    
    "bot" {
        Write-Host "Running bot processing tests..." -ForegroundColor Yellow
        pytest tests/test_bot_api.py -v
    }
    
    "rag" {
        Write-Host "Running RAG tests..." -ForegroundColor Yellow
        pytest tests/test_rag_api.py -v
    }
    
    "conversations" {
        Write-Host "Running conversation tests..." -ForegroundColor Yellow
        pytest tests/test_conversations_api.py -v
    }
    
    "flows" {
        Write-Host "Running user flow tests..." -ForegroundColor Yellow
        pytest tests/test_user_flows.py -v
    }
    
    "parallel" {
        Write-Host "Running tests in parallel..." -ForegroundColor Yellow
        try {
            $null = Get-Command pytest-xdist -ErrorAction Stop
            pytest tests/ -v -n auto
        } catch {
            Write-Host "Error: pytest-xdist is not installed" -ForegroundColor Red
            Write-Host "Install with: pip install pytest-xdist"
            exit 1
        }
    }
    
    "quick" {
        Write-Host "Running quick smoke tests..." -ForegroundColor Yellow
        pytest tests/ -v -k "health or root" --tb=short
    }
    
    "help" {
        Write-Host "Usage: .\run_tests.ps1 [option]"
        Write-Host ""
        Write-Host "Options:"
        Write-Host "  all          - Run all tests (default)"
        Write-Host "  unit         - Run only unit tests"
        Write-Host "  integration  - Run only integration tests"
        Write-Host "  smoke        - Run smoke tests"
        Write-Host "  coverage     - Run tests with coverage report"
        Write-Host "  config       - Run configuration API tests"
        Write-Host "  bot          - Run bot processing tests"
        Write-Host "  rag          - Run RAG API tests"
        Write-Host "  conversations - Run conversation management tests"
        Write-Host "  flows        - Run user flow tests"
        Write-Host "  parallel     - Run tests in parallel (requires pytest-xdist)"
        Write-Host "  quick        - Run quick smoke tests"
        Write-Host "  help         - Show this help message"
    }
    
    default {
        Write-Host "Error: Unknown option '$RunType'" -ForegroundColor Red
        Write-Host "Run '.\run_tests.ps1 help' for usage information"
        exit 1
    }
}

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Tests completed successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Tests failed" -ForegroundColor Red
    exit 1
}

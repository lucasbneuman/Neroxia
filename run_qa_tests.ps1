$ErrorActionPreference = "Continue"

# Get current date in dd_MM_yyyy format
$date = Get-Date -Format "dd_MM_yyyy"

# Create test_results directory if it doesn't exist
$resultsDir = "test_results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
    Write-Host "Created directory: $resultsDir" -ForegroundColor Green
}

Write-Host "Starting QA Test Run..." -ForegroundColor Cyan
Write-Host "Reports will be saved to: $resultsDir" -ForegroundColor Cyan

# 1. API Unit Tests
Write-Host "`n[1/3] Running API Unit Tests..." -ForegroundColor Yellow
$unitReport = "$resultsDir\unit_api_$date.html"
cd apps/api
python -m pytest tests/unit/ -v --html="..\..\$unitReport" --self-contained-html
if ($LASTEXITCODE -eq 0) { Write-Host "API Unit Tests Passed" -ForegroundColor Green }
else { Write-Host "API Unit Tests Failed (Check Report)" -ForegroundColor Red }
cd ..\..

# 2. API Integration Tests
Write-Host "`n[2/3] Running API Integration Tests..." -ForegroundColor Yellow
$integrationReport = "$resultsDir\integration_api_$date.html"
cd apps/api
python -m pytest tests/integration/ -v --html="..\..\$integrationReport" --self-contained-html
if ($LASTEXITCODE -eq 0) { Write-Host "API Integration Tests Passed" -ForegroundColor Green }
else { Write-Host "API Integration Tests Failed (Check Report)" -ForegroundColor Red }
cd ..\..

# 3. Bot Engine Tests
Write-Host "`n[3/3] Running Bot Engine Tests..." -ForegroundColor Yellow
$botReport = "$resultsDir\bot_engine_$date.html"
cd apps/bot-engine
python -m pytest tests/ -v --html="..\..\$botReport" --self-contained-html
if ($LASTEXITCODE -eq 0) { Write-Host "Bot Engine Tests Passed" -ForegroundColor Green }
else { Write-Host "Bot Engine Tests Failed (Check Report)" -ForegroundColor Red }
cd ..\..

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "HTML Reports generated:" -ForegroundColor White
Write-Host " - Unit Tests: $unitReport" -ForegroundColor Gray
Write-Host " - Integration Tests: $integrationReport" -ForegroundColor Gray
Write-Host " - Bot Engine Tests: $botReport" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan

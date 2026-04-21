# WhatsApp Sales Bot SaaS - Development Startup Script
# For Windows PowerShell

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " WhatsApp Sales Bot SaaS - Development Mode" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Please edit .env with your API keys before continuing." -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
    }
}

$webEnvPath = "apps/web/.env.local"
if ((Test-Path ".env") -and (-not (Test-Path $webEnvPath))) {
    Write-Host "Creating frontend env from root .env..." -ForegroundColor Yellow
    $rootEnv = @{}
    Get-Content ".env" | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $key, $value = $line.Split("=", 2)
            $rootEnv[$key.Trim()] = $value.Trim()
        }
    }

    $frontendEnv = @(
        "NEXT_PUBLIC_API_URL=$($rootEnv["NEXT_PUBLIC_API_URL"])",
        "NEXT_PUBLIC_SUPABASE_URL=$($rootEnv["NEXT_PUBLIC_SUPABASE_URL"])",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY=$($rootEnv["NEXT_PUBLIC_SUPABASE_ANON_KEY"])"
    )
    Set-Content -Path $webEnvPath -Value $frontendEnv
}

# Create data directory if it doesn't exist
if (-not (Test-Path "data")) {
    Write-Host "Creating data directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path "data" | Out-Null
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start API Backend
Write-Host "[1/2] Starting API Backend..." -ForegroundColor Cyan
$apiProcess = Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Write-Host 'API Backend Starting...' -ForegroundColor Green; cd apps/api; python -m uvicorn src.main:app --reload --port 8000"
) -PassThru

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend..." -ForegroundColor Cyan
$webProcess = Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Write-Host 'Frontend Starting...' -ForegroundColor Green; cd apps/web; npm run dev"
) -PassThru

Write-Host ""
Write-Host "=================================================" -ForegroundColor Green
Write-Host " Services Started Successfully!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop services" -ForegroundColor Yellow
Write-Host ""

# Keep script running
Write-Host "Press any key to stop all services..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

# Stop processes
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $webProcess.Id -Force -ErrorAction SilentlyContinue

Write-Host "All services stopped." -ForegroundColor Green

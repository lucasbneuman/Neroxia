#!/bin/bash

# Neroxia SaaS - Development Startup Script
# For Linux/Mac

echo "================================================="
echo " Neroxia SaaS - Development Mode"
echo "================================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "   WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env with your API keys before continuing."
        read -p "Press Enter to continue..."
    fi
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

echo ""
echo "Starting services..."
echo ""

# Start API Backend
echo "[1/2] Starting API Backend..."
cd apps/api
python -m uvicorn src.main:app --reload --port 8000 &
API_PID=$!
cd ../..

sleep 3

# Start Frontend
echo "[2/2] Starting Frontend..."
cd apps/web
npm run dev &
WEB_PID=$!
cd ../..

echo ""
echo "================================================="
echo " Services Started Successfully!"
echo "================================================="
echo ""
echo "API Backend:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend:     http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to stop both processes
trap "echo 'Stopping services...'; kill $API_PID $WEB_PID 2>/dev/null; echo 'All services stopped.'; exit 0" INT

# Wait for both processes
wait

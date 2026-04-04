@echo off
echo Starting MIT Faculty AI...

:: Start Backend
start cmd /k "echo Starting Backend... && py -3.13 backend/main.py"

:: Start Frontend
start cmd /k "echo Starting Frontend... && cd frontend && npm run dev"

echo Backend and Frontend are starting in separate windows.
echo Please ensure you have added your ANTHROPIC_API_KEY to backend/.env
echo Access the UI at: http://localhost:5173

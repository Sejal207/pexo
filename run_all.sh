#!/usr/bin/env bash
set -e

# Ensure PostgreSQL and Redis are running locally.
# If you use Homebrew, you can start them with:
#   brew services start postgresql@18 redis
# Otherwise, start them manually before running this script.

run_service() {
  SERVICE=$1
  PORT=$2
  SCHEMA=$3
  SERVICE_DIR="$(pwd)/services/$SERVICE"
  if [ ! -d "$SERVICE_DIR" ]; then
    echo "Service directory not found: $SERVICE_DIR"
    exit 1
  fi
  cd "$SERVICE_DIR"
  # Create virtual environment if missing
  if [ ! -d .venv ]; then
    python -m venv .venv
  fi
  source .venv/bin/activate
  # Install dependencies
  pip install -r requirements.txt
  # Copy example env if .env missing
  # Ensure .env exists (handled manually)
  # Set default env vars
  export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/Pexo"
  export DB_SCHEMA="$SCHEMA"
  export REDIS_URL="redis://localhost:6379/0"
  export SECRET_KEY="supersecretjwtkey_change_in_production_Pexo"
  # API gateway needs service URLs
  if [ "$SERVICE" = "api-gateway" ]; then
    export HR_SERVICE_URL="http://localhost:8001"
    export ATTENDANCE_SERVICE_URL="http://localhost:8002"
    export PAYROLL_SERVICE_URL="http://localhost:8003"
  fi
  # Logs directory
  LOG_DIR="$(pwd)/../../logs"
  mkdir -p "$LOG_DIR"
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload > "${LOG_DIR}/${SERVICE}.log" 2>&1 &
  echo "$SERVICE started on port $PORT (log: logs/${SERVICE}.log)"
  cd - > /dev/null
}

# Create logs folder at workspace root
mkdir -p logs

# Start backend services
run_service hr-service 8001 hr
run_service attendance-timeoff-service 8002 attendance_timeoff
run_service payroll-service 8003 payroll
run_service api-gateway 8000 gateway

# Frontend
cd "$(pwd)/frontend"
npm install
npm run dev

#!/usr/bin/env bash
set -euo pipefail

# Weather Enrichment Service launcher for Linux/macOS.
# It starts the whole stack with Docker Compose and opens the frontend.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

FRONTEND_URL="http://localhost:4200"
BACKEND_HEALTH_URL="http://localhost:8000/health"

print_header() {
  printf '\n========================================\n'
  printf ' Weather Enrichment Service launcher\n'
  printf '========================================\n\n'
}

fail() {
  printf '\nERROR: %s\n' "$1" >&2
  if [ -t 0 ]; then
    printf '\nPress Enter to close...'
    read -r _ || true
  fi
  exit 1
}

find_compose() {
  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
  elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
  else
    fail "Docker Compose was not found. Install Docker Desktop or Docker Engine with Compose."
  fi
}

open_browser() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$FRONTEND_URL" >/dev/null 2>&1 || true
  elif command -v gio >/dev/null 2>&1; then
    gio open "$FRONTEND_URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$FRONTEND_URL" >/dev/null 2>&1 || true
  else
    printf 'Could not auto-open browser. Open this URL manually:\n%s\n' "$FRONTEND_URL"
  fi
}

wait_for_backend() {
  printf 'Waiting for backend health check at %s ...\n' "$BACKEND_HEALTH_URL"
  for _ in $(seq 1 60); do
    if command -v curl >/dev/null 2>&1 && curl -fsS "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
      printf 'Backend is ready.\n'
      return 0
    fi
    sleep 2
  done
  printf 'Backend did not answer yet. Containers may still be starting.\n'
  return 0
}

print_header

command -v docker >/dev/null 2>&1 || fail "Docker was not found. Install Docker Desktop or Docker Engine first."
docker info >/dev/null 2>&1 || fail "Docker is installed, but the Docker daemon is not running. Start Docker Desktop or Docker service first."
find_compose

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  printf 'Created .env from .env.example\n'
fi

printf 'Starting containers from:\n%s\n\n' "$ROOT_DIR"
"${COMPOSE_CMD[@]}" up -d --build

wait_for_backend

printf '\nApplication is running.\n'
printf 'Frontend:    %s\n' "$FRONTEND_URL"
printf 'API docs:    http://localhost:8000/docs\n'
printf 'Health:      %s\n\n' "$BACKEND_HEALTH_URL"

open_browser

printf 'Useful commands from this folder:\n'
printf '  docker compose ps\n'
printf '  docker compose logs -f backend\n'
printf '  docker compose logs -f celery_worker\n'
printf '  docker compose down\n\n'

if [ -t 0 ]; then
  printf 'Press Enter to close this launcher. The app will keep running in Docker...'
  read -r _ || true
fi

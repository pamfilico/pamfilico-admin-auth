#!/bin/bash
# Orchestrator: boot docker-compose test stack, wait for health, run pytest, tear down.
# Mirrors packages/flask-collection/run-tests.sh per the codespec test harness convention.
set -e
cd "$(dirname "$0")"

FRONTEND_FLAG="${RUN_FRONTEND:-0}"

COMPOSE_SERVICES="db api"
if [ "$FRONTEND_FLAG" = "1" ]; then
  COMPOSE_SERVICES="db api frontend"
fi

echo "Starting test stack ($COMPOSE_SERVICES)..."
docker compose -f docker-compose.test.yml up -d --build $COMPOSE_SERVICES

echo "Waiting for PostgreSQL..."
for i in {1..30}; do
  if docker compose -f docker-compose.test.yml exec -T db pg_isready -U test -d testdb 2>/dev/null; then
    echo "PostgreSQL ready."
    break
  fi
  [ $i -eq 30 ] && { echo "PostgreSQL failed."; docker compose -f docker-compose.test.yml down; exit 1; }
  sleep 1
done

echo "Waiting for API..."
for i in {1..30}; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:5098/health 2>/dev/null | grep -q 200; then
    echo "API ready."
    break
  fi
  [ $i -eq 30 ] && { echo "API failed."; docker compose -f docker-compose.test.yml logs api; docker compose -f docker-compose.test.yml down; exit 1; }
  sleep 1
done

if [ "$FRONTEND_FLAG" = "1" ]; then
  echo "Waiting for frontend..."
  for i in {1..60}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3098/ 2>/dev/null | grep -q -E "200|307"; then
      echo "Frontend ready."
      break
    fi
    [ $i -eq 60 ] && { echo "Frontend failed."; docker compose -f docker-compose.test.yml logs frontend; docker compose -f docker-compose.test.yml down; exit 1; }
    sleep 1
  done
fi

export ADMIN_AUTH_TEST_API_URL=http://localhost:5098

poetry run pytest -v
EXIT_CODE=$?

docker compose -f docker-compose.test.yml down
echo "Done."
exit $EXIT_CODE

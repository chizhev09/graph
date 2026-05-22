#!/bin/bash
# На сервере: cd /opt/graph && bash scripts/deploy_from_git.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> git pull"
git pull origin main

echo "==> swap (если нет)"
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
fi

echo "==> build (celery_worker с Playwright — долго)"
export DOCKER_BUILDKIT=1
docker compose build celery_worker
docker compose build

echo "==> up"
docker compose up -d

echo "==> migrations"
docker compose exec -T backend alembic upgrade head

echo "==> status"
docker compose ps -a
docker compose exec -T celery_worker test -d /ms-playwright/chromium-* && echo "Playwright OK" || echo "Playwright MISSING"

curl -fsS http://127.0.0.1/api/health || true

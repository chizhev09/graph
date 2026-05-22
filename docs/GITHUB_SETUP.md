# GitHub Setup Guide

## 1. Инициализация репозитория

```bash
cd Graph
git init
git add .
git commit -m "Initial commit: Graph production backend and frontend"
```

## 2. Подключение GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/graph.git
git branch -M main
git push -u origin main
```

## 3. .gitignore

**Не коммитить:**

- `backend/.env`
- `backend/.venv/`
- `backend/data/telegram_session*`
- `frontend/node_modules/`
- `frontend/dist/`

## 4. Секреты

- `BOT_TOKEN`
- `JWT_SECRET`
- `DATABASE_URL` (postgresql+asyncpg://graph:graph@...)
- `TELEGRAM_API_ID` / `TELEGRAM_API_HASH`
- `WEBSHARE_PROXIES`
- `PREMIUM_CHANNEL_ID`

## 5. Обновление production

```bash
ssh user@server
cd /opt/graph
git pull origin main
python backend/scripts/sync_categories.py
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

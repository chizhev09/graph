# Production Commands

## Docker Compose

```bash
docker compose up -d --build
docker compose down
docker compose restart backend
docker compose logs -f backend
docker compose logs -f celery_worker
```

## Database

```bash
docker compose exec backend alembic upgrade head
docker compose exec postgres psql -U graph -d graph
docker compose exec postgres pg_dump -U graph graph > backup.sql
```

## Redis

```bash
docker compose exec redis redis-cli
docker compose exec redis redis-cli FLUSHDB
```

## Celery

```bash
docker compose restart celery_worker celery_beat
docker compose exec celery_worker celery -A app.workers.celery_app inspect active
```

## Categories sync

```bash
python backend/scripts/sync_categories.py
```

## Monitoring

- API: `GET /api/health`
- Swagger: `/docs`

# Деплой Graph на Timeweb VPS

Пошаговая инструкция: очистка сервера по SSH и установка приложения.

---

## 1. Подключение по SSH

Данные для входа — в панели Timeweb: **Серверы → ваш VPS → SSH**.

```bash
ssh root@ВАШ_IP_СЕРВЕРА
```

Или с паролем/ключом от пользователя, если уже создан.

---

## 2. Очистка сервера (осторожно)

### 2.1. Посмотреть, что занято

```bash
# Запущенные Docker-контейнеры
docker ps -a

# Старые проекты
ls -la /opt
ls -la /var/www

# Сервисы
systemctl list-units --type=service --state=running | grep -E 'nginx|apache|docker'
```

### 2.2. Остановить старые Docker-проекты

Если на сервере был другой проект в Docker:

```bash
cd /opt/СТАРЫЙ_ПРОЕКТ   # если знаете путь
docker compose down -v   # -v удалит volumes (БД тоже!)
```

Или остановить всё Docker:

```bash
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null
```

### 2.3. Очистить Docker (освободить место)

```bash
docker system prune -a --volumes -f
```

**Внимание:** удалит все неиспользуемые образы, контейнеры и volumes.

### 2.4. Удалить старые файлы проекта (по желанию)

```bash
rm -rf /opt/snpr
rm -rf /opt/old_project
rm -rf /var/www/html/*
```

Не трогайте `/etc/ssh`, системные каталоги.

### 2.5. Остановить системный nginx (если мешает порту 80)

Наше приложение использует nginx в Docker на порту **80**.

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
```

Если Timeweb требует свой nginx — настройте прокси на `127.0.0.1:80` (см. раздел 8).

---

## 3. Подготовка сервера

### 3.1. Обновление системы

```bash
apt update && apt upgrade -y
```

### 3.2. Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin git nano
usermod -aG docker $USER
```

Перелогиньтесь (выйти из SSH и зайти снова), чтобы группа `docker` применилась.

### 3.3. Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

---

## 4. Загрузка проекта на сервер

### Вариант A: через GitHub (рекомендуется)

На **вашем ПК** сначала залейте код в GitHub (см. `docs/GITHUB_SETUP.md`).

На **сервере**:

```bash
mkdir -p /opt/graph
cd /opt/graph
git clone https://github.com/ВАШ_USERNAME/graph.git .
```

### Вариант B: без GitHub (архив с ПК)

На **ПК** (PowerShell):

```powershell
cd c:\Users\chizh\Desktop\Snpr
# исключите .env, .venv, node_modules — они в .gitignore
git archive -o graph.zip HEAD   # если git init сделан
# или заархивируйте папку вручную без node_modules и .venv
scp graph.zip root@ВАШ_IP:/opt/
```

На **сервере**:

```bash
cd /opt
unzip graph.zip -d graph
cd graph
```

---

## 5. Настройка `.env` на сервере

```bash
cd /opt/graph
cp backend/.env.example backend/.env
nano backend/.env
```

**Обязательно заполните:**

```env
DEBUG=false
ENVIRONMENT=production

# Внутри Docker сеть — НЕ меняйте хост postgres:
DATABASE_URL=postgresql+asyncpg://graph:graph@postgres:5432/graph

REDIS_URL=redis://redis:6379/0

BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
PREMIUM_CHANNEL_ID=-100...

JWT_SECRET=длинный_случайный_ключ_32_символа_минимум

CORS_ORIGINS=https://ваш-домен.ru
WEB_APP_URL=https://ваш-домен.ru

DEFAULT_CITY=moscow
```

Сохранить: `Ctrl+O`, Enter, `Ctrl+X`.

Синхронизация категорий:

```bash
python3 backend/scripts/sync_categories.py
# или из контейнера после первого build — см. ниже
```

---

## 6. Запуск приложения

### Если ошибка `unauthenticated pull rate limit` (Docker Hub)

**Вариант 1 — залогиниться в Docker Hub (бесплатно):**

```bash
docker login
# логин/пароль с https://hub.docker.com
docker compose pull
docker compose up -d --build
```

**Вариант 2 — образы уже из Amazon ECR Public** (в `docker-compose.yml`), обновите проект:

```bash
cd /opt/graph
git pull
docker compose pull
docker compose up -d --build
```

```bash
cd /opt/graph
docker compose up -d --build
```

Проверка:

```bash
docker compose ps
docker compose logs -f backend
curl http://localhost/api/health
```

Должно вернуть: `{"status":"ok",...}`

Сервисы:
- **nginx** — порты 80 (сайт + API)
- **backend** — API, Swagger `/docs`
- **postgres**, **redis**, **celery**

Telegram listener (опционально, после настройки Telethon):

```bash
docker compose --profile telegram up -d telegram_listener
```

---

## 7. Домен и Telegram Mini App

### 7.1. DNS в Timeweb

Панель Timeweb → **Домены** → A-запись на IP вашего VPS.

### 7.2. BotFather

1. @BotFather → ваш бот → **Bot Settings** → **Menu Button** → URL: `https://ваш-домен.ru`
2. **Configure Mini App** → URL: `https://ваш-домен.ru`

### 7.3. HTTPS (SSL) — Certbot + Docker nginx

На VPS (домен `pushes.su` → IP сервера):

```bash
apt install -y certbot
mkdir -p /var/www/certbot

# 1) Временно HTTP-конфиг (см. docker/nginx/nginx.init.conf) — для webroot
cp docker/nginx/nginx.init.conf docker/nginx/nginx.conf
docker compose up -d --force-recreate nginx

# 2) Выпуск сертификата
certbot certonly --webroot -w /var/www/certbot \
  -d pushes.su -d www.pushes.su \
  --email admin@pushes.su --agree-tos --non-interactive

# 3) Полный HTTPS-конфиг (docker/nginx/nginx.conf) + порты 80/443 в compose
docker compose up -d --force-recreate nginx
```

В `docker-compose.yml` для nginx:

- порты `80:80`, `443:443`
- тома `/var/www/certbot`, `/etc/letsencrypt`

Автообновление: cron `certbot renew` + hook `docker compose restart nginx`.

Проверка: `https://pushes.su/api/health` → `{"status":"ok",...}`

---

## 8. Если порт 80 занят системным nginx

Файл `/etc/nginx/sites-available/graph`:

```nginx
server {
    listen 80;
    server_name ваш-домен.ru;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

И в `docker-compose.yml` смените nginx ports на `"8080:80"`.

---

## 9. Полезные команды

```bash
cd /opt/graph

# Логи
docker compose logs -f backend
docker compose logs -f celery_worker

# Перезапуск
docker compose restart backend celery_worker celery_beat

# Обновление после git pull
git pull origin main
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head

# Playwright (только в celery_worker, образ Dockerfile.workers)
docker compose exec celery_worker playwright --version
docker compose exec celery_worker ls /ms-playwright

# Бэкап БД
docker compose exec postgres pg_dump -U graph graph > backup_$(date +%Y%m%d).sql
```

---

## 10. Чеклист после деплоя

- [ ] `https://ваш-домен.ru` открывает Mini App
- [ ] `https://ваш-домен.ru/api/health` → ok
- [ ] `https://ваш-домен.ru/docs` — Swagger
- [ ] Бот: Mini App открывается из Telegram
- [ ] `docker compose ps` — все сервисы Up

---

## Минимальные требования VPS

- **RAM:** 2 GB+ (лучше 4 GB с Playwright/Celery)
- **Диск:** 20 GB+
- **ОС:** Ubuntu 22.04 / 24.04

# Timeweb VPS Deployment

## Server setup

```bash
ssh root@YOUR_SERVER_IP
adduser graph
usermod -aG sudo graph
su - graph
```

### Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo apt install docker-compose-plugin -y
```

### Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Deploy project

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/graph.git
cd graph
cp backend/.env.example backend/.env
nano backend/.env
python3 backend/scripts/sync_categories.py
docker compose up -d --build
```

## SSL

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

## Backup PostgreSQL

```bash
docker compose exec postgres pg_dump -U graph graph > backup_$(date +%Y%m%d).sql
```

## Обновление

```bash
git pull
python3 backend/scripts/sync_categories.py
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

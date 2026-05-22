# FlowMind 部署文档

## 系统要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.10 | 3.12+ |
| Node.js | 18.0 | 20+ |
| MySQL | 5.7 | 8.0+ |
| Redis | 6.0 | 7.0+ |
| 内存 | 2GB | 4GB+ |
| 磁盘 | 1GB | 5GB+ |

## 环境变量配置

创建 `backend/.env` 文件：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=flowmind

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 安全配置
SECRET_KEY=change-this-to-a-random-string-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 调试模式（生产环境请设为 false）
DEBUG=false
```

## 数据库初始化

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE flowmind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建专用用户（推荐）
CREATE USER 'flowmind'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON flowmind.* TO 'flowmind'@'localhost';
FLUSH PRIVILEGES;
```

## 后端部署

### 方式一：直接运行

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 数据库表由应用启动时自动创建
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 方式二：Docker 部署

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t flowmind-backend ./backend
docker run -d -p 8000:8000 --env-file backend/.env flowmind-backend
```

### 方式三：Systemd 服务（Linux）

```ini
# /etc/systemd/system/flowmind.service
[Unit]
Description=FlowMind Backend
After=network.target mysql.service redis.service

[Service]
Type=exec
User=www-data
WorkingDirectory=/opt/FlowMind/backend
EnvironmentFile=/opt/FlowMind/backend/.env
ExecStart=/opt/FlowMind/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable flowmind
sudo systemctl start flowmind
```

## 前端部署

### 开发环境

```bash
cd frontend
npm install
npm run dev
```

### 生产环境构建

```bash
cd frontend
npm install
npm run build
```

构建产物位于 `frontend/dist/`，使用 Nginx 托管：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/flowmind/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Nginx 反向代理（完整配置）

```nginx
upstream flowmind_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/flowmind/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # API 代理
    location /api/ {
        proxy_pass http://flowmind_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 限流
        limit_req zone=api burst=20 nodelay;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        root /var/www/flowmind/dist;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Redis 配置优化

```conf
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 数据备份策略

```bash
#!/bin/bash
# backup.sh - 每日数据库备份
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/flowmind"
mkdir -p $BACKUP_DIR

mysqldump -u flowmind -p flowmind | gzip > "$BACKUP_DIR/flowmind_$DATE.sql.gz"

# 保留最近30天
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

设置定时任务：

```bash
crontab -e
# 每天凌晨3点执行备份
0 3 * * * /opt/FlowMind/scripts/backup.sh
```

## 性能优化建议

1. **MySQL**：为常用查询字段添加索引（owner_id, status, created_at）
2. **Redis**：使用连接池，避免频繁创建连接
3. **FastAPI**：生产环境使用 gunicorn + uvicorn worker
4. **前端**：启用 Gzip 压缩，配置 CDN 缓存静态资源
5. **Nginx**：配置限流防止 API 滥用

## 监控建议

- 使用 Prometheus + Grafana 监控 API 响应时间和错误率
- 配置 MySQL 慢查询日志
- Redis INFO 命令监控内存使用
- 应用日志使用 ELK Stack 或 Loki 收集分析

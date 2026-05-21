# AIFriends 部署指南（Claude 用）

> 最后更新：2026-05-21
> 服务器：121.43.36.186 (Ubuntu 24.04)
> 域名：app6809.acapp.acwing.com.cn

## 服务器连接方式

```python
import paramiko

host = "121.43.36.186"
username = "acs"
password = "12138"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(host, username=username, password=password, timeout=10)
```

本地 Python 环境：`D:/coding_software/anaconda3/envs/Claude/python.exe`

## 项目概述

- 后端：Django 6.0 + DRF + SimpleJWT + SQLite
- 前端：Vue 3 + Vite + TailwindCSS v4 + daisyUI v5
- 部署方式：Nginx → Gunicorn(Unix socket) → Django

## 项目文件路径

| 内容 | 路径 |
|------|------|
| 后端代码 | `/home/acs/aifriends/backend/` |
| 静态文件 | `/home/acs/aifriends/backend/static/` |
| 前端构建输出 | `/home/acs/aifriends/backend/static/frontend/` |
| 媒体文件 | `/home/acs/aifriends/backend/media/` |
| 数据库 SQLite | `/home/acs/aifriends/backend/db.sqlite3` |
| Nginx 配置 | `/etc/nginx/nginx.conf` |
| Gunicorn socket | `/home/acs/aifriends/backend/gunicorn.sock` |
| Python venv | `/home/acs/aifriends/backend/venv/` |

## 部署步骤

### 第一步：本地构建前端

```bash
cd frontend
npm run build
```

构建产物自动输出到 `../backend/static/frontend/`。

### 第二步：准备 settings.py

生产环境通过环境变量控制：

```python
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '默认key')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'app6809.acapp.acwing.com.cn', '121.43.36.186']
CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173', 'https://app6809.acapp.acwing.com.cn']
```

### 第三步：上传到服务器

通过 paramiko SFTP 上传 `backend/` 目录到 `/home/acs/aifriends/backend/`。

**不要上传**：`__pycache__/`、`db.sqlite3`（如有旧数据需保留则上传）、`venv/`、`media/` 里的旧文件。

### 第四步：服务器环境初始化（仅首次）

```bash
# 安装 python3-venv
echo '12138' | sudo -S apt-get install -y python3.12-venv

# 创建虚拟环境
cd /home/acs/aifriends/backend
python3 -m venv venv

# 安装依赖（用阿里云镜像，服务器无法直连 PyPI）
./venv/bin/pip install -i https://mirrors.aliyun.com/pypi/simple/ \
  --trusted-host mirrors.aliyun.com -r requirements.txt
```

### 第五步：数据库迁移和静态文件

```bash
cd /home/acs/aifriends/backend

# 迁移
./venv/bin/python manage.py migrate --run-syncdb

# 收集静态文件
mkdir -p static
./venv/bin/python manage.py collectstatic --noinput

# 创建管理员（首次）
./venv/bin/python manage.py shell
# >>> from django.contrib.auth import get_user_model
# >>> User = get_user_model()
# >>> User.objects.create_superuser('admin', 'admin@example.com', '12138')
```

### 第六步：启动 Gunicorn（tmux）

```bash
# 删除旧会话
tmux kill-session -t aifriends

# 创建新会话
tmux new-session -d -s aifriends

# 发送启动命令
tmux send-keys -t aifriends \
  "cd /home/acs/aifriends/backend && \
   DJANGO_SECRET_KEY='django-insecure-ft9=+wgt^=mzdw%d58j^f\$tkp)lxc3%)1d%auhs%m6qrll#*r5' \
   DJANGO_DEBUG=False \
   ./venv/bin/gunicorn --workers 3 --graceful-timeout 30 \
   --bind unix:/home/acs/aifriends/backend/gunicorn.sock \
   backend.wsgi:application" Enter
```

### 第七步：配置 Nginx

```nginx
user acs;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    access_log /var/log/nginx/access.log;
    gzip on;
    gzip_disable "msie6";

    server {
        listen 80;
        server_name app6809.acapp.acwing.com.cn;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name app6809.acapp.acwing.com.cn;
        ssl_certificate     /etc/nginx/cert/acapp.pem;
        ssl_certificate_key /etc/nginx/cert/acapp.key;
        ssl_session_timeout 5m;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;

        # JS/CSS 资源（前端构建产物）
        location /assets/ {
            alias /home/acs/aifriends/backend/static/frontend/assets/;
            expires 30d;
        }

        # Django 静态文件（admin 等）
        location /static/ {
            alias /home/acs/aifriends/backend/static/;
            expires 30d;
        }

        # 用户上传的媒体文件
        location /media/ {
            alias /home/acs/aifriends/backend/media/;
            expires 30d;
        }

        # API + SPA fallback → Gunicorn
        location / {
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://unix:/home/acs/aifriends/backend/gunicorn.sock;
        }
    }

    # 注意：sites-enabled/default 必须删除，否则会覆盖
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

```bash
# 删除默认站点（关键！否则 blank page）
echo '12138' | sudo -S rm -f /etc/nginx/sites-enabled/default

# 应用配置
echo '12138' | sudo -S cp /tmp/nginx.conf /etc/nginx/nginx.conf
echo '12138' | sudo -S nginx -t
echo '12138' | sudo -S nginx -s reload
```

## 故障排查

### 空白页面
- 检查 `/etc/nginx/sites-enabled/default` 是否已删除
- 检查 `/assets/` location 是否配置（Nginx 配置第 7 步）
- curl 测试：`curl -sk https://localhost/assets/index-xxx.js`

### Gunicorn 未运行
```bash
ps aux | grep gunicorn | grep -v grep
tmux attach -t aifriends  # 看错误日志
```

### 静态文件 404
```bash
ls -la /home/acs/aifriends/backend/static/frontend/assets/
```

### 重启步骤
```bash
# 1. Kill gunicorn
ps aux | grep gunicorn | grep -v grep | awk '{print $2}' | xargs -r kill -9
rm -f /home/acs/aifriends/backend/gunicorn.sock

# 2. 重新启动（按第六步）
```

## 旧项目

旧项目位于 `/home/acs/backend/`，已停止但文件保留。如需恢复运行需还原 `/etc/nginx/nginx.conf` 中的 server block 路径至 `/home/acs/backend/`。

# Nginx 配置记录

服务器：Linux
域名：ablog.axingit.top
配置文件路径：`/etc/nginx/sites-available/blog`

## 当前完整配置

```nginx
server {
    server_name ablog.axingit.top;
    root /var/www/blog;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 静态资源缓存（排除/daily和/entertainment路径）
    location ~* ^(?!/daily|/entertainment).*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # ===== Daily System 项目 =====
    # 前端静态文件
    location /daily {
        alias /var/www/daily-system/reading-system/frontend/dist;
        index index.html;
        try_files $uri $uri/ /daily/index.html;
    }

    # Daily System 静态资源
    location /daily/assets/ {
        alias /var/www/daily-system/reading-system/frontend/dist/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Daily System API 代理
    location /daily/api/ {
        rewrite ^/daily/api/(.*)$ /api/$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ===== Entertainment 项目 =====
    # 前端静态文件
    location /entertainment {
        alias /var/www/entertainment/frontend/dist;
        index index.html;
        try_files $uri $uri/ /entertainment/index.html;
    }

    # Entertainment 静态资源
    location /entertainment/assets/ {
        alias /var/www/entertainment/frontend/dist/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Entertainment API 代理
    location /entertainment/api/ {
        rewrite ^/entertainment/api/(.*)$ /api/$1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Entertainment WebSocket 代理
    location /entertainment/ws/ {
        rewrite ^/entertainment/ws/(.*)$ /ws/$1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # ===== 博客项目（原有配置）=====
    location / {
        try_files $uri $uri/ /index.html;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/ablog.axingit.top/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/ablog.axingit.top/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = ablog.axingit.top) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name ablog.axingit.top;
    return 404; # managed by Certbot
}
```

## 项目路径说明

| 项目 | 前端路径 | 后端端口 | 访问地址 |
|------|----------|----------|----------|
| Blog | /var/www/blog | - | https://ablog.axingit.top/ |
| Daily System | /var/www/daily-system/reading-system/frontend/dist | 8000 | https://ablog.axingit.top/daily |
| Entertainment | /var/www/entertainment/frontend/dist | 8001 | https://ablog.axingit.top/entertainment |

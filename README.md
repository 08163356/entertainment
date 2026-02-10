# Entertainment 娱乐工具集

一个集成多种娱乐活动工具的 Web 应用，首期功能为**台球记分系统**。

## 功能特性

### 台球记分
- 🎱 实时记分，支持多人同步观看
- 📊 自动统计局数、球数、金额
- 👥 房间系统，支持权限控制
- 📈 个人战绩统计和图表分析
- 🎨 多主题切换（浅色/深色/台球绿/皇家蓝）
- 📱 响应式设计，支持全屏模式

## 技术栈

| 前端 | 后端 |
|------|------|
| Vue 3 + TypeScript | Python FastAPI |
| TDesign UI | SQLite + SQLAlchemy |
| Pinia | WebSocket |
| ECharts | |

## 本地开发

### 环境要求
- Node.js >= 18
- Python >= 3.9

### 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

开发环境访问: http://localhost:3000/entertainment/

## 服务器部署

### 1. 构建前端

```bash
cd frontend
npm run build
```

将 `dist` 目录上传到服务器，如 `/var/www/entertainment/`

### 2. 部署后端

```bash
cd backend
pip install -r requirements.txt

# 使用 gunicorn 生产部署
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

# 或使用 systemd 服务管理
```

**创建 systemd 服务 `/etc/systemd/system/entertainment.service`:**

```ini
[Unit]
Description=Entertainment API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable entertainment
sudo systemctl start entertainment
```

### 3. Nginx 配置

在 Nginx 配置中添加：

```nginx
# 台球记分系统
location /entertainment/ {
    alias /var/www/entertainment/;
    try_files $uri $uri/ /entertainment/index.html;
}

# API 代理
location /entertainment/api/ {
    rewrite ^/entertainment/api/(.*)$ /api/$1 break;
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# WebSocket 代理
location /entertainment/ws/ {
    rewrite ^/entertainment/ws/(.*)$ /ws/$1 break;
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 访问

部署完成后访问: https://ablog.axingit.top/entertainment

## 项目结构

```
entertainment/
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # Pinia 状态
│   │   ├── services/       # API 和 WebSocket
│   │   ├── types/          # TypeScript 类型
│   │   └── styles/         # 全局样式
│   └── package.json
│
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   ├── models.py       # 数据模型
│   │   └── main.py         # 应用入口
│   └── requirements.txt
│
└── docs/                    # 文档
    └── 台球记分系统-需求与实现.md
```

## API 文档

启动后端后访问: http://localhost:8000/docs

## License

MIT

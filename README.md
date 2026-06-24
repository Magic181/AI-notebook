# AI Notebook

AI 知识工作台 — 上传资料、AI 阅读、智能问答、引用原文。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Tailwind CSS |
| 后端 | Django + DRF + JWT |
| 数据库 | MySQL / SQLite（开发回退） |
| 缓存 | Redis |

## 快速开始

### 1. 启动基础服务（可选）

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 2. 后端

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
cp ../.env.example .env   # 默认 USE_SQLITE=true，无需 Docker 即可启动
python manage.py migrate
python manage.py runserver
```

后端默认运行在 http://localhost:8000

### 3. 前端

```bash
cd frontend
pnpm install
pnpm dev
```

前端默认运行在 http://localhost:5173，API 请求通过 Vite 代理转发到后端。

## 项目结构

```
AI-Notebook/
├── docs/           # 产品 & 技术文档
├── frontend/       # Vue3 前端
├── backend/        # Django 后端
├── docker-compose.dev.yml
└── .env.example
```

## 文档

- [产品路线图](docs/product/产品路线图.md)
- [需求文档](docs/product/需求文档.md)
- [架构设计](docs/engineering/架构设计.md)
- [API 规范](docs/engineering/API规范.md)

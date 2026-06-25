# AI Notebook

AI 知识工作台 — 上传资料、AI 阅读、智能问答、引用原文。

## 当前进度

| 模块 | 状态 | 说明 |
|------|------|------|
| 项目基础 | ✅ 已完成 | Django + Vue3 脚手架、Docker Compose、统一 API 格式 |
| 用户认证 | ✅ 已完成 | 注册/登录/刷新/退出、JWT 黑名单、启动会话校验 |
| Notebook 管理 | ✅ 已完成 | CRUD、收藏、搜索、分页 |
| 文档管理 | ✅ 已完成 | 上传、解析、分块、状态追踪（TXT/MD/PDF/DOCX） |
| AI 聊天 + RAG | ✅ 已完成 | 会话、消息、关键词 RAG、引用来源、DeepSeek 调用 |
| 联网搜索 | ✅ 已完成 | 本地资料 / 联网搜索 / 混合模式、网页来源引用 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Tailwind CSS + Element Plus |
| 后端 | Django 5 + DRF + SimpleJWT |
| 数据库 | MySQL（推荐）/ SQLite（本地快速启动） |
| 队列 | Celery + Redis（开发可用 eager 模式） |
| AI | DeepSeek OpenAI-compatible API + Tavily Search |

## 快速开始

### 1. 环境准备

- Python 3.12+
- Node.js 22 LTS + pnpm 10+
- MySQL 8.0（或使用 SQLite 模式）

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，配置数据库、JWT、DeepSeek 和 Tavily（详见 [环境配置](docs/devops/环境配置.md)）。

本地快速体验建议：

```env
USE_SQLITE=true
CELERY_TASK_ALWAYS_EAGER=true
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=
TAVILY_API_KEY=
```

### 3. 启动后端

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**可选 — Celery Worker（`CELERY_TASK_ALWAYS_EAGER=false` 时）：**

```bash
celery -A config worker -l info
```

后端默认运行在 http://localhost:8000

### 4. 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

前端默认运行在 http://localhost:5173，API 通过 Vite 代理转发到后端。

### 5. 可选：Docker 基础服务

```bash
docker compose -f docker-compose.dev.yml up -d
```

提供 MySQL + Redis，端口见 `docker-compose.dev.yml`。

## 项目结构

```
AI-Notebook/
├── docs/                    # 产品 & 技术文档
├── frontend/                # Vue3 前端
│   └── src/
│       ├── api/             # API 封装
│       ├── layouts/         # 布局组件
│       ├── pages/           # 页面
│       └── stores/          # Pinia 状态
├── backend/                 # Django 后端
│   └── apps/
│       ├── core/            # 健康检查、统一响应
│       ├── users/           # 用户认证
│       ├── notebooks/       # 笔记本 CRUD
│       ├── documents/       # 文档上传与解析
│       └── chat/            # AI 会话、RAG、联网搜索
├── docker-compose.dev.yml
└── .env.example
```

## 已实现 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health/` | 健康检查 |
| POST | `/api/v1/auth/register/` | 注册（自动返回 token） |
| POST | `/api/v1/auth/login/` | 登录 |
| POST | `/api/v1/auth/refresh/` | 刷新 token |
| POST | `/api/v1/auth/logout/` | 退出（黑名单 refresh token） |
| GET | `/api/v1/auth/me/` | 当前用户信息 |
| GET/POST | `/api/v1/notebooks/` | 列表 / 创建 |
| GET/PATCH/DELETE | `/api/v1/notebooks/{id}/` | 详情 / 更新 / 删除 |
| POST | `/api/v1/notebooks/{id}/favorite/` | 切换收藏 |
| GET/POST | `/api/v1/notebooks/{id}/documents/` | 文档列表 / 上传 |
| GET/DELETE | `/api/v1/documents/{id}/` | 文档详情 / 删除 |
| GET/POST | `/api/v1/notebooks/{id}/conversations/` | 会话列表 / 创建 |
| GET | `/api/v1/conversations/{id}/messages/` | 消息列表 |
| POST | `/api/v1/conversations/{id}/messages/send/` | 发送消息，支持本地 / 联网 / 混合搜索模式 |

## 测试

```powershell
# 后端系统检查与聚焦测试
$env:USE_SQLITE='true'
backend\venv\Scripts\python.exe backend\manage.py check
backend\venv\Scripts\python.exe backend\manage.py test apps.chat apps.documents

# 前端类型检查
cd frontend
cmd /c node_modules\.bin\vue-tsc.cmd --noEmit
```

完整规范见 [API 规范](docs/engineering/API规范.md)。

## 文档

- [产品路线图](docs/product/产品路线图.md)
- [需求文档](docs/product/需求文档.md)
- [架构设计](docs/engineering/架构设计.md)
- [API 规范](docs/engineering/API规范.md)
- [数据库设计](docs/engineering/数据库设计.md)
- [环境配置](docs/devops/环境配置.md)

## 仓库

https://github.com/Magic181/AI-notebook

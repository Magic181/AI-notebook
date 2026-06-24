# AI Notebook

AI 知识工作台 — 上传资料、AI 阅读、智能问答、引用原文。

## 当前进度

| 模块 | 状态 | 说明 |
|------|------|------|
| 项目基础 | ✅ 已完成 | Django + Vue3 脚手架、Docker Compose、统一 API 格式 |
| 用户认证 | ✅ 已完成 | 注册/登录/刷新/退出、JWT 黑名单、启动会话校验 |
| Notebook 管理 | ✅ 已完成 | CRUD、收藏、搜索、分页 |
| 文档管理 | ⏳ 待开发 | Batch 4 |
| AI 聊天 + RAG | ⏳ 待开发 | Batch 5 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Tailwind CSS + Element Plus |
| 后端 | Django 5 + DRF + SimpleJWT |
| 数据库 | MySQL（推荐）/ SQLite（本地快速启动） |
| 缓存 | Redis（规划中，文档/AI 批次使用） |

## 快速开始

### 1. 环境准备

- Python 3.12+
- Node.js 22 LTS + pnpm 10+
- MySQL 8.0（或使用 SQLite 模式）

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，配置数据库与 JWT（详见 [环境配置](docs/devops/环境配置.md)）。

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
│       └── notebooks/       # 笔记本 CRUD
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

# AI Notebook Kit

AI Notebook Kit 是一个可复用的 AI 知识库 Starter Kit，而不是只能运行单一业务形态的示例应用。它把常见 AI SaaS 的基础能力打包好：账号体系、Notebook、文档上传、解析分块、OCR、视觉描述、RAG 问答、联网搜索、引用溯源、Landing Page、演示站和 Docker 一键部署。

## 你会得到什么

| 模块 | 能力 |
|------|------|
| 品牌与演示 | Logo 组件、Landing Page、公开首页、登录后 Demo 应用区 |
| 前端应用 | Vue 3 + Vite + Pinia + Tailwind CSS + Element Plus |
| 后端 API | Django 5 + DRF + SimpleJWT + 统一响应格式 + 限流 |
| 知识库 | Notebook CRUD、收藏、搜索、文档上传、解析状态追踪 |
| AI 能力 | DeepSeek/OpenAI-compatible Chat、RAG、Tavily 联网搜索、引用来源 |
| 多模态 | PDF/DOCX/TXT/MD 解析、图片资产、OCR、可选视觉描述 |
| 任务队列 | Celery + Redis，支持本地 eager 模式 |
| 部署 | 生产 Dockerfile、Nginx 反向代理、Docker Compose 全栈编排 |

## 快速预览

```bash
cp .env.example .env
docker compose up -d --build
```

打开：

- Landing Page: `http://localhost:8080`
- Demo 应用: `http://localhost:8080/app`
- API 健康检查: `http://localhost:8080/api/v1/health/`

首次进入 Demo 可以注册账号。需要后台管理员时执行：

```bash
docker compose exec backend python manage.py createsuperuser
```

## 本地开发

后端：

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

前端：

```bash
cd frontend
pnpm install
pnpm dev
```

本地开发默认地址：

- 前端: `http://localhost:5173`
- 后端: `http://localhost:8000`

如果只想启动 MySQL 和 Redis：

```bash
docker compose -f docker-compose.dev.yml up -d
```

## 推荐目录

```text
AI-Notebook/
├── backend/                 # Django API、Celery、文档解析、RAG
│   ├── apps/
│   │   ├── core/            # 健康检查、统一响应、异常处理、限流
│   │   ├── users/           # 注册、登录、JWT、当前用户
│   │   ├── notebooks/       # Notebook CRUD、收藏、搜索
│   │   ├── documents/       # 上传、解析、OCR、视觉描述、资产
│   │   └── chat/            # 会话、消息、RAG、联网搜索、LLM 调用
│   ├── config/              # Django、Celery、URL 配置
│   └── Dockerfile
├── frontend/
│   ├── public/assets/       # Landing 视觉资产
│   ├── src/
│   │   ├── api/             # API 客户端
│   │   ├── components/      # 品牌、UI、业务组件
│   │   ├── composables/     # 流式聊天等组合逻辑
│   │   ├── layouts/         # 登录后应用框架
│   │   ├── pages/           # Landing、认证、Notebook、Chat
│   │   ├── router/          # 公开页与 /app 应用区路由
│   │   ├── stores/          # Pinia 状态
│   │   └── styles/          # 设计 token 与全局样式
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                    # 产品、工程、AI、设计、运维文档
├── docker-compose.yml       # 生产式一键部署
├── docker-compose.dev.yml   # 开发依赖服务
└── .env.example
```

## 自定义 Starter Kit

1. 改品牌：调整 `frontend/src/components/brand/StarterLogo.vue`、Landing 文案和 `frontend/public/assets/starter-hero.png`。
2. 改应用壳：公开页在 `/`，登录后应用在 `/app`，可把 Notebook 产品替换为自己的业务模块。
3. 改 AI Provider：在 `.env` 中替换 `DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`、`DEEPSEEK_API_KEY`。
4. 改搜索：配置 `TAVILY_API_KEY` 后可使用联网搜索或混合检索。
5. 改解析能力：通过 `OCR_*` 和 `VISION_*` 环境变量启用 OCR 与视觉描述。

## 常用命令

```bash
# 前端
cd frontend
pnpm typecheck
pnpm lint
pnpm test
pnpm build

# 后端
cd backend
python manage.py check
python manage.py test apps.chat apps.documents apps.notebooks apps.users

# Docker
docker compose up -d --build
docker compose logs -f backend
docker compose down
```

Docker 一键部署使用 `DOCKER_MYSQL_*` 变量，避免和本地开发的 `MYSQL_USER=root` 等配置冲突。

## 文档

- [Starter Kit 使用指南](docs/STARTER_KIT.md)
- [部署指南](docs/devops/部署指南.md)
- [环境配置](docs/devops/环境配置.md)
- [架构设计](docs/engineering/架构设计.md)
- [API 规范](docs/engineering/API规范.md)
- [RAG 架构](docs/ai/RAG架构.md)

## 仓库

https://github.com/Magic181/AI-notebook

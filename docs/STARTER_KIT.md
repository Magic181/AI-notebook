# Starter Kit 使用指南

> 最后更新：2026-07-09

AI Notebook Kit 的目标是提供一个可继续扩展的 AI 知识产品底座。它保留了一个完整 Demo，但代码结构、路由和部署方式都按 Starter Kit 组织，方便你替换品牌、产品模块和 AI Provider。

## 核心形态

| 区域 | 路径 | 说明 |
|------|------|------|
| Landing Page | `/` | 公开介绍页，展示品牌、能力、技术栈和部署方式 |
| 认证页 | `/login`, `/register` | Starter Demo 的账号入口 |
| Demo 应用 | `/app` | 登录后的 Notebook、文档和聊天体验 |
| API | `/api/v1/` | Django REST API |
| Admin | `/admin/` | Django 管理后台 |

## 品牌定制

品牌入口集中在：

- `frontend/src/components/brand/StarterLogo.vue`
- `frontend/src/pages/Landing.vue`
- `frontend/public/assets/starter-hero.png`
- `frontend/index.html`

建议先替换：

1. Logo 标题和副标题。
2. Landing 的 H1、价值描述和功能卡片。
3. Hero 图片。
4. README 中的项目名、仓库地址和部署域名。

## 产品模块替换

登录后应用从 `/app` 开始，核心页面在 `frontend/src/pages/`：

- `Home.vue`: Notebook 列表与创建入口。
- `Notebook.vue`: 文档上传、文档列表、重新解析。
- `Chat.vue`: 会话、消息、RAG 问答和联网搜索。

后端按 Django app 拆分：

- `apps.users`: 账号与 JWT。
- `apps.notebooks`: 工作区或业务容器。
- `apps.documents`: 文件、解析、OCR、视觉描述。
- `apps.chat`: 会话、RAG、搜索模式、LLM 服务。

如果你要做新的 AI SaaS，通常保留 `users`、`core`、`documents`、`chat`，把 `notebooks` 改名或包一层业务概念即可。

## AI Provider

聊天模型使用 OpenAI-compatible 接口。常用变量：

```env
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=
DEEPSEEK_TIMEOUT_SECONDS=60
```

联网搜索：

```env
TAVILY_API_KEY=
TAVILY_MAX_RESULTS=5
TAVILY_SEARCH_DEPTH=basic
```

视觉描述：

```env
VISION_ENABLED=false
VISION_PROVIDER=openai_compatible
VISION_BASE_URL=https://api.openai.com/v1
VISION_MODEL=gpt-4o-mini
VISION_API_KEY=
```

## 部署路径

生产式本地验证：

```bash
cp .env.example .env
docker compose up -d --build
```

Compose 服务：

| 服务 | 说明 |
|------|------|
| `frontend` | Nginx 托管前端静态文件，并反向代理 `/api` 和 `/admin` |
| `backend` | Django + Gunicorn API |
| `worker` | Celery 文档解析和异步任务 |
| `mysql` | MySQL 8 数据库 |
| `redis` | Celery broker/result backend |

## 发布前检查

```bash
cd frontend
pnpm typecheck
pnpm lint
pnpm build

cd ../backend
python manage.py check
python manage.py test apps.chat apps.documents apps.notebooks apps.users
```

服务器发布时至少修改：

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CORS_ALLOWED_ORIGINS`
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- AI Provider API Key

## 裁剪建议

- 只做本地知识库：保留 `documents` 和 `chat`，关闭 `TAVILY_API_KEY`。
- 做企业知识库：接入对象存储，把 `MEDIA_ROOT` 替换为 S3/MinIO 适配层。
- 做多租户 SaaS：给 Notebook 增加 workspace/team 维度，并把权限逻辑下沉到 queryset。
- 做插件化 AI 产品：保留 `/app` 框架，把 Notebook 页面替换为新的业务页面。

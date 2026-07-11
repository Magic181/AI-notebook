# Starter Kit 使用指南

> 最后更新：2026-07-10

MindBase Kit 是 AI 产品工程底座，不是只能继续开发成 Notebook 的单一应用。仓库内保留 Knowledge Demo，用来验证认证、摄取、解析、检索、引用和流式对话链路；其他业务可以复用同一套基础设施。

## 能力状态

| 类型 | 含义 | 当前模块 |
|---|---|---|
| Wired | 后端、前端与运行链路均已接通 | Auth、Knowledge ingestion、RAG chat、Operations |
| Adapter | 提供 UI contract 和推荐边界，需要接入自己的服务 | Team & access、Billing |

公开页面与工作台会直接展示这个区别，避免把静态 Demo 数据包装成已经完成的商业功能。

## 前端结构

```text
frontend/src/
├── app/
│   ├── App.vue
│   ├── router.ts
│   └── layouts/AppShell.vue
├── config/starter.ts
├── features/
│   ├── marketing/
│   ├── auth/
│   ├── dashboard/
│   ├── knowledge/
│   ├── chat/
│   ├── admin/
│   └── billing/
├── components/
├── api/
├── stores/
└── styles/
```

- `app/` 只负责应用启动、路由和壳层。
- `config/starter.ts` 集中保存品牌、导航、仓库地址和模块 manifest。
- `features/` 按用户可见能力组织页面。
- `components/` 放跨 feature 复用的 UI、导航和领域组件。
- `api/` 与 `stores/` 保持稳定，页面重组不改变接口契约。

## 第一次定制

### 1. 品牌与导航

优先修改：

- `frontend/src/config/starter.ts`
- `frontend/src/components/brand/StarterLogo.vue`
- `frontend/public/favicon.svg`
- `frontend/index.html`
- `frontend/src/styles/main.css`

设计 token 已集中到 `main.css` 的 CSS variables。更换颜色、圆角、阴影和明暗主题时，不需要逐页搜索硬编码颜色。

### 2. 删除不需要的 surface

路由集中在 `frontend/src/app/router.ts`。删除 feature 时同时移除：

1. `features/<name>/` 页面。
2. `config/starter.ts` 的导航和模块声明。
3. `app/router.ts` 的路由。
4. 对应后端 app（仅当没有其他模块依赖它）。

Team 与 Billing 默认是 optional surface，可以直接裁剪。

### 3. 替换 Demo 领域

Knowledge Demo 使用 Notebook 作为业务容器。新产品通常可以：

- 保留 `users`、`core`、`documents` 和 `chat`。
- 将 `notebooks` 替换为 Project、Case、Customer、Workspace 等领域对象。
- 继续复用摄取、chunk、OCR、引用与流式回答能力。

## Provider boundaries

聊天模型走 OpenAI-compatible 配置：

```env
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=
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

对象存储、权限与计费建议保持同样的 adapter 思路，不要把 provider SDK 直接散落在 view 或页面里。

## 运行与发布

```bash
cp .env.example .env
docker compose up -d --build
```

Compose 包含 frontend、backend、worker、mysql 和 redis。发布前至少修改密钥、域名、数据库密码和 AI provider 配置。

## 检查

```bash
cd frontend
pnpm typecheck
pnpm lint
pnpm test
pnpm build

cd ../backend
python manage.py check
python manage.py test apps.chat apps.documents apps.notebooks apps.users
```

生成目录、coverage、临时浏览器截图和测试报告不应提交到仓库；测试源码本身需要保留。README 中的发布级演示素材属于例外，但必须由当前版本重新录制，UI 变更后不得继续复用旧素材。

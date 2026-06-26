# API 规范

> 最后更新：2026-06-25

## 基础规范

### URL 格式

```
/api/v1/{resource}
```

### HTTP 方法

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 查询 | `GET /api/v1/notebooks/` |
| POST | 创建 / 动作 | `POST /api/v1/notebooks/` |
| PUT | 全量更新 | `PUT /api/v1/notebooks/1/` |
| PATCH | 部分更新 | `PATCH /api/v1/notebooks/1/` |
| DELETE | 删除 | `DELETE /api/v1/notebooks/1/` |

### 状态码约定

- **HTTP 状态码**表示请求成败（200/201/400/401/404 等）
- **响应 body 中的 `code`** 与 HTTP 状态码对齐
- 业务细分错误码（如 `1001=用户名已存在`）后续版本引入

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 / 退出登录 |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未认证 / Token 无效 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Server Error | 服务器错误 |

## 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "Notebook 名称",
    "created_at": "2026-06-18T12:00:00Z"
  }
}
```

### 列表响应（分页）

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "参数错误",
  "errors": [
    {
      "field": "name",
      "message": "名称不能为空"
    }
  ],
  "data": null
}
```

---

## 认证 API

所有需认证接口在 Header 中携带：

```http
Authorization: Bearer <access_token>
```

### 注册

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "user1",
  "email": "user@example.com",
  "password": "password123"
}
```

**响应 201：**

```json
{
  "code": 201,
  "message": "success",
  "data": {
    "access": "<access_token>",
    "refresh": "<refresh_token>"
  }
}
```

注册成功后直接返回 token，前端自动登录。

### 登录

```http
POST /api/v1/auth/login/

{
  "username": "user1",
  "password": "password123"
}
```

**响应 200：** 同注册，返回 `access` + `refresh`。

### 刷新 Token

```http
POST /api/v1/auth/refresh/

{
  "refresh": "<refresh_token>"
}
```

**响应 200：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access": "<new_access_token>",
    "refresh": "<new_refresh_token>"
  }
}
```

启用 Token 轮换：刷新后旧 refresh token 失效。

### 退出登录

```http
POST /api/v1/auth/logout/
Authorization: Bearer <access_token>

{
  "refresh": "<refresh_token>"
}
```

**响应 204：** 无 body。refresh token 加入黑名单。

### 当前用户

```http
GET /api/v1/auth/me/
Authorization: Bearer <access_token>
```

**响应 200：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user1",
    "email": "user@example.com"
  }
}
```

### JWT 配置（环境变量）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| JWT_ACCESS_TOKEN_MINUTES | 5 | Access Token 有效期（分钟） |
| JWT_REFRESH_TOKEN_DAYS | 7 | Refresh Token 有效期（天） |

---

## Notebook API

用户只能访问自己创建的笔记本。

### 列表

```http
GET /api/v1/notebooks/?search=关键词&is_favorite=true&page=1&page_size=20&ordering=-updated_at
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| search | string | - | 搜索名称、描述 |
| is_favorite | bool | - | `true` 时仅返回收藏 |
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量（最大 100） |
| ordering | string | -updated_at | 排序：`created_at`、`-created_at`、`updated_at`、`-updated_at`、`name`、`-name` |

**响应 200：** 分页列表格式，`items` 中每项：

```json
{
  "id": 1,
  "name": "我的笔记本",
  "description": "描述",
  "is_favorite": false,
  "document_count": 0,
  "created_at": "2026-06-18T12:00:00Z",
  "updated_at": "2026-06-18T12:00:00Z"
}
```

> `document_count` 当前由后端按关联文档数量返回。

### 创建

```http
POST /api/v1/notebooks/

{
  "name": "我的笔记本",
  "description": "可选描述"
}
```

**响应 201：** 返回完整 Notebook 对象。

### 详情

```http
GET /api/v1/notebooks/{id}/
```

**响应 200：** 返回 Notebook 对象。非本人资源返回 404。

### 更新

```http
PATCH /api/v1/notebooks/{id}/

{
  "name": "新名称",
  "description": "新描述"
}
```

**响应 200：** 返回更新后的 Notebook 对象。

### 删除

```http
DELETE /api/v1/notebooks/{id}/
```

**响应 204：** 无 body。硬删除。

### 切换收藏

```http
POST /api/v1/notebooks/{id}/favorite/
```

**响应 200：** 返回切换后的 Notebook 对象（`is_favorite` 已翻转）。

---

## Document API

### 文档列表

```http
GET /api/v1/notebooks/{notebook_id}/documents/
Authorization: Bearer <access_token>
```

**响应 200：**

```json
[
  {
    "id": 1,
    "notebook_id": 1,
    "name": "notes.md",
    "file_type": "md",
    "file_size": 1024,
    "status": "completed",
    "chunk_count": 3,
    "error_message": "",
    "created_at": "2026-06-25T08:00:00+08:00",
    "updated_at": "2026-06-25T08:00:00+08:00"
  }
]
```

### 上传文档

```http
POST /api/v1/notebooks/{notebook_id}/documents/
Content-Type: multipart/form-data

files=<file1>&files=<file2>
```

支持：TXT、MD、PDF、DOCX。后端会先校验整批文件，再保存并触发解析任务，避免部分成功。

### 文档详情 / 删除

```http
GET /api/v1/documents/{id}/
DELETE /api/v1/documents/{id}/
```

用户只能访问自己 Notebook 下的文档。

---

## Chat API

### 会话列表

```http
GET /api/v1/notebooks/{notebook_id}/conversations/
```

### 创建会话

```http
POST /api/v1/notebooks/{notebook_id}/conversations/

{
  "title": "可选标题"
}
```

### 消息列表

```http
GET /api/v1/conversations/{conversation_id}/messages/
```

### 删除会话

```http
DELETE /api/v1/conversations/{conversation_id}/
```

**响应 204：** 无 body。只允许删除当前用户自己 Notebook 下的会话，消息会随会话级联删除。

### 发送消息

```http
POST /api/v1/conversations/{conversation_id}/messages/send/

{
  "content": "请总结这份资料",
  "search_mode": "local"
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| content | string | 必填 | 用户问题 |
| search_mode | string | local | `local` 只查 Notebook，`web` 只联网搜索，`hybrid` 混合搜索 |
| web_search | boolean | false | 旧字段，兼容保留；`true` 等价于 `search_mode=hybrid` |

**响应 200：**

```json
{
  "user_message": {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "请总结这份资料",
    "citations": [],
    "created_at": "2026-06-25T08:00:00+08:00"
  },
  "assistant_message": {
    "id": 2,
    "conversation_id": 1,
    "role": "assistant",
    "content": "回答内容",
    "citations": [
      {
        "source_type": "document",
        "document_id": 1,
        "document_name": "notes.md",
        "chunk_id": 1,
        "chunk_text": "原文片段",
        "position": 0
      },
      {
        "source_type": "web",
        "title": "网页标题",
        "url": "https://example.com",
        "content": "网页摘要",
        "position": 1
      }
    ],
    "created_at": "2026-06-25T08:00:02+08:00"
  }
}
```

`local` 模式只使用 Notebook 内已解析文档和模型通用能力；`web` 模式只使用 Tavily 联网搜索结果；`hybrid` 模式会同时使用 Notebook 文档片段和 Tavily 搜索结果。网页结果会作为 `[W1]`、`[W2]` 等来源加入上下文。

---

## 系统 API

### 健康检查

```http
GET /api/v1/health/
```

无需认证。

**响应 200：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "ai-notebook-api",
    "version": "0.1.0"
  }
}
```

---

## 版本控制

- URL 路径版本：`/api/v1/`、`/api/v2/`
- 当前版本：**v1**

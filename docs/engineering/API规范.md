# API 规范

> 最后更新：2026-06-24

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

> `document_count` 当前固定返回 0，Batch 4 接入文档后更新。

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

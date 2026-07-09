# AI Notebook Kit 文档目录

> 最后更新：2026-07-09

本目录记录 AI Notebook Kit 当前真实可运行的 Starter Kit 能力、工程约定和部署方式。

## 快速入口

| 类别 | 文档 | 适合场景 |
|------|------|----------|
| Starter Kit | [Starter Kit 使用指南](STARTER_KIT.md) | 定制品牌、替换模块、理解 `/` 与 `/app` 的分层 |
| 产品 | [需求文档](product/需求文档.md) | 理解目标用户、核心流程和长期规划 |
| 产品 | [产品路线图](product/产品路线图.md) | 查看批次进度、已完成能力和后续方向 |
| 工程 | [架构设计](engineering/架构设计.md) | 理解前后端、文档解析、RAG 和 AI 服务边界 |
| 工程 | [API 规范](engineering/API规范.md) | 对接 REST API、确认请求响应字段 |
| 工程 | [数据库设计](engineering/数据库设计.md) | 查看核心表、索引和数据关系 |
| 工程 | [编码规范](engineering/编码规范.md) | 统一后端、前端和 Git 协作规则 |
| AI | [RAG 架构](ai/RAG架构.md) | 理解结构化检索、重排、OCR 和视觉描述如何进入问答 |
| 设计 | [UI 规范](design/UI规范.md) | 统一界面密度、按钮、卡片和交互表达 |
| 运维 | [环境配置](devops/环境配置.md) | 配置 `.env`、数据库、Redis、AI、OCR、视觉模型 |
| 运维 | [部署指南](devops/部署指南.md) | 本地开发、Docker 一键部署、验证和故障排查 |

## 当前目录边界

- `STARTER_KIT.md`: 面向二次开发者的定制入口。
- `product/`: 产品目标、路线图和规划。
- `engineering/`: 当前代码结构、API、数据库和协作约定。
- `ai/`: RAG、联网搜索、OCR、视觉描述和回答策略。
- `design/`: 前端体验和 UI 约束。
- `devops/`: 可执行的环境配置、启动、部署和排障步骤。

## 文档维护规则

- 新增环境变量时同步更新 `.env.example` 和 [环境配置](devops/环境配置.md)。
- 新增接口时同步更新 [API 规范](engineering/API规范.md)。
- 调整解析、检索、引用或 AI Provider 时同步更新 [RAG 架构](ai/RAG架构.md)。
- 调整 Starter Kit 路由、品牌入口或部署方式时同步更新 [Starter Kit 使用指南](STARTER_KIT.md)。

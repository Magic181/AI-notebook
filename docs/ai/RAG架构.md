# RAG架构设计

## 概述

RAG (Retrieval-Augmented Generation) 是 AI Notebook 的核心能力，通过检索用户文档来增强 LLM 的回答质量。当前实现为轻量版本：文档解析、文本分块、关键词检索、Prompt 构建、DeepSeek 生成回答，并支持 Tavily 联网搜索作为可选外部资料来源。

## 架构流程

```
用户问题
    │
    ▼
┌─────────────────┐
│  Query Process  │  问题预处理、关键词提取
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Local Retrieval │  Notebook 文档关键词检索
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Web Search      │  可选 Tavily 联网搜索
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Context Building │  本地片段 + 网页结果
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generate   │  DeepSeek 生成回答
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Citation     │  文档 / 网页来源
└─────────────────┘
```

## 模块设计

### 当前实现

| 模块 | 文件 | 说明 |
|------|------|------|
| 文档解析 | `backend/apps/documents/parsers.py` | TXT/MD/PDF/DOCX 文本提取 |
| 文本分块 | `backend/apps/documents/chunking.py` | 按段落和固定长度分块 |
| 本地检索 | `backend/apps/chat/rag.py` | 基于关键词 `icontains` 检索文档片段 |
| 联网搜索 | `backend/apps/chat/web_search.py` | Tavily Search，返回标题、摘要、链接 |
| LLM 调用 | `backend/apps/chat/rag.py` | DeepSeek OpenAI-compatible Chat API |
| 来源展示 | `Message.citations` | `document` 和 `web` 两类来源 |

### 规划中的向量化升级

### Embedding Service

```python
class EmbeddingService:
    """向量化服务"""
    
    def embed_text(self, text: str) -> List[float]:
        """单条文本向量化"""
        
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
```

支持的模型：
- OpenAI text-embedding-3-small/large
- 本地模型 (Ollama)

### Vector Store

```python
class VectorStore:
    """向量存储接口"""
    
    def insert(self, id: str, vector: List[float], metadata: dict):
        """插入向量"""
        
    def search(self, vector: List[float], top_k: int = 10) -> List[SearchResult]:
        """相似度搜索"""
        
    def delete(self, ids: List[str]):
        """删除向量"""
```

支持的存储：
- Milvus (生产)
- ChromaDB (开发)

### Reranker

```python
class Reranker:
    """重排序服务"""
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """重排序"""
```

### RAG Pipeline

```python
class RAGPipeline:
    """RAG流水线"""
    
    def __init__(self, embedding, vector_store, reranker, llm):
        self.embedding = embedding
        self.vector_store = vector_store
        self.reranker = reranker
        self.llm = llm
    
    async def query(self, question: str, notebook_id: int) -> RAGResponse:
        """执行RAG查询"""
        # 1. 问题向量化
        # 2. 向量检索
        # 3. 重排序
        # 4. 构建上下文
        # 5. LLM生成
        # 6. 标注引用
```

## 检索策略

### 当前基础检索

- 对用户问题做简单 token 化
- 在当前 Notebook 已完成解析的 `DocumentChunk.content` 中做关键词匹配
- 取 Top K 片段并按关键词命中次数排序

### 当前联网搜索

- 前端 Chat 页面选择“联网搜索”或“混合”模式
- 后端按 `search_mode` 决定是否调用 Tavily Search
- 搜索结果作为 `[W1]`、`[W2]` 加入上下文
- 回答中可展示网页来源链接

### 后续混合检索

- 向量搜索 + 关键词搜索
- 分数融合

### 多路召回

- 语义检索
- 关键词检索
- 元数据过滤

## 分块策略

### 固定大小分块

- 块大小：512 tokens
- 重叠：50 tokens

### 语义分块

- 按段落/章节分割
- 保持语义完整性

### 递归分块

- 先按大结构分割
- 再按小结构细分

## 引用标注

### 引用格式

```json
[
  {
    "source_type": "document",
    "document_id": 1,
    "document_name": "论文.pdf",
    "chunk_id": 5,
    "chunk_text": "原文片段...",
    "position": 4
  },
  {
    "source_type": "web",
    "title": "网页标题",
    "url": "https://example.com",
    "content": "网页摘要...",
    "position": 1
  }
]
```

### 引用链接

- 支持点击跳转到原文位置
- 高亮显示引用内容

当前前端已支持网页来源点击打开链接；本地文档片段定位和高亮属于后续优化项。

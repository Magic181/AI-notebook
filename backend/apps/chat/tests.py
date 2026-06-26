from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from requests import exceptions as request_exceptions
from rest_framework import status
from rest_framework.test import APIClient

from apps.documents.models import Document, DocumentChunk, DocumentStatus
from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .rag import Citation, DeepSeekAuthError, build_prompt, call_deepseek_chat, retrieve_citations
from .services import (
    AI_FAILURE_MESSAGE,
    WEB_ONLY_SEARCH_DEGRADED_MESSAGE,
    WEB_SEARCH_DEGRADED_MESSAGE,
    build_citation_payload,
)
from .web_search import WebResult, WebSearchError, search_web


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=''):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class ConversationSendMessageTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='chat-user',
            email='chat@example.com',
            password='test-password',
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            name='Chat notebook',
        )
        self.conversation = Conversation.objects.create(
            notebook=self.notebook,
            title='Failure path',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('apps.chat.services.logger')
    @patch('apps.chat.services.call_deepseek_chat', side_effect=RuntimeError('service down'))
    def test_ai_failure_preserves_user_message_and_returns_assistant_failure(
        self,
        _,
        logger,
    ):
        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': 'Summarize this notebook'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        messages = list(Message.objects.order_by('created_at'))
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, MessageRole.USER)
        self.assertEqual(messages[0].content, 'Summarize this notebook')
        self.assertEqual(messages[1].role, MessageRole.ASSISTANT)
        self.assertEqual(messages[1].content, AI_FAILURE_MESSAGE)
        self.assertEqual(messages[1].citations, [])

        self.assertEqual(response.data['user_message']['id'], messages[0].id)
        self.assertEqual(response.data['assistant_message']['id'], messages[1].id)
        logger.exception.assert_called_once()

    @patch('apps.chat.services.search_web')
    @patch('apps.chat.services.retrieve_citations', return_value=[])
    @patch('apps.chat.services.call_deepseek_chat', return_value='这是联网搜索回答。')
    def test_send_message_with_web_search_saves_web_sources(
        self,
        _,
        retrieve_citations,
        search_web,
    ):
        search_web.return_value = [
            WebResult(
                title='Example result',
                url='https://example.com/article',
                content='Search result summary.',
                position=1,
            )
        ]

        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '搜索最新资料', 'search_mode': 'web'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrieve_citations.assert_not_called()
        search_web.assert_called_once_with('搜索最新资料')

        assistant = Message.objects.filter(role=MessageRole.ASSISTANT).latest('id')
        self.assertEqual(assistant.content, '这是联网搜索回答。')
        self.assertEqual(assistant.citations[0]['source_type'], 'web')
        self.assertEqual(assistant.citations[0]['url'], 'https://example.com/article')

    @patch('apps.chat.services.search_web')
    @patch('apps.chat.services.retrieve_citations', return_value=[])
    @patch('apps.chat.services.call_deepseek_chat', return_value='这是混合搜索回答。')
    def test_hybrid_search_uses_local_and_web_sources(
        self,
        _,
        retrieve_citations,
        search_web,
    ):
        search_web.return_value = []

        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '混合搜索问题', 'search_mode': 'hybrid'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrieve_citations.assert_called_once_with(self.notebook.id, '混合搜索问题', top_k=5)
        search_web.assert_called_once_with('混合搜索问题')

    @patch('apps.chat.services.search_web')
    @patch('apps.chat.services.retrieve_citations', return_value=[])
    @patch('apps.chat.services.call_deepseek_chat', return_value='兼容旧参数。')
    def test_legacy_web_search_flag_maps_to_hybrid_mode(
        self,
        _,
        retrieve_citations,
        search_web,
    ):
        search_web.return_value = []

        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '旧参数问题', 'web_search': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrieve_citations.assert_called_once_with(self.notebook.id, '旧参数问题', top_k=5)
        search_web.assert_called_once_with('旧参数问题')

    @patch('apps.chat.services.logger')
    @patch('apps.chat.services.search_web', side_effect=WebSearchError('search unavailable'))
    @patch('apps.chat.services.call_deepseek_chat', return_value='这是本地资料回答。')
    def test_web_search_failure_degrades_to_local_answer(
        self,
        _,
        search_web,
        logger,
    ):
        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '搜索最新资料', 'web_search': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        search_web.assert_called_once_with('搜索最新资料')
        logger.warning.assert_called_once()

        assistant = Message.objects.filter(role=MessageRole.ASSISTANT).latest('id')
        self.assertIn(WEB_SEARCH_DEGRADED_MESSAGE, assistant.content)
        self.assertIn('这是本地资料回答。', assistant.content)
        self.assertEqual(assistant.citations, [])

    @patch('apps.chat.services.logger')
    @patch('apps.chat.services.search_web', side_effect=WebSearchError('search unavailable'))
    @patch('apps.chat.services.call_deepseek_chat', return_value='这是通用能力回答。')
    def test_web_only_search_failure_uses_web_only_degraded_message(
        self,
        _,
        search_web,
        logger,
    ):
        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '搜索最新资料', 'search_mode': 'web'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        search_web.assert_called_once_with('搜索最新资料')
        logger.warning.assert_called_once()

        assistant = Message.objects.filter(role=MessageRole.ASSISTANT).latest('id')
        self.assertIn(WEB_ONLY_SEARCH_DEGRADED_MESSAGE, assistant.content)
        self.assertIn('这是通用能力回答。', assistant.content)
        self.assertEqual(assistant.citations, [])

    @patch('apps.chat.services.retrieve_citations', return_value=[])
    @patch('apps.chat.services.call_deepseek_chat', return_value='可以接着回答。')
    def test_follow_up_message_includes_recent_history(
        self,
        call_deepseek_chat,
        retrieve_citations,
    ):
        Message.objects.create(
            conversation=self.conversation,
            role=MessageRole.USER,
            content='我上传的文件你能读到吗',
            citations=[],
        )
        Message.objects.create(
            conversation=self.conversation,
            role=MessageRole.ASSISTANT,
            content='暂时没有读到资料片段。',
            citations=[],
        )

        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': '现在呢'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrieve_citations.assert_called_once_with(
            self.notebook.id,
            '我上传的文件你能读到吗\n现在呢',
            top_k=5,
        )
        messages = call_deepseek_chat.call_args.args[0]
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], '我上传的文件你能读到吗')
        self.assertEqual(messages[2]['role'], 'assistant')
        self.assertEqual(messages[2]['content'], '暂时没有读到资料片段。')
        self.assertIn('用户问题：现在呢', messages[-1]['content'])


class ConversationDeleteTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='delete-user',
            email='delete@example.com',
            password='test-password',
        )
        self.other_user = user_model.objects.create_user(
            username='other-delete-user',
            email='other-delete@example.com',
            password='test-password',
        )
        self.notebook = Notebook.objects.create(user=self.user, name='Delete notebook')
        self.other_notebook = Notebook.objects.create(
            user=self.other_user,
            name='Other notebook',
        )
        self.conversation = Conversation.objects.create(
            notebook=self.notebook,
            title='Delete me',
        )
        Message.objects.create(
            conversation=self.conversation,
            role=MessageRole.USER,
            content='hello',
            citations=[],
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_delete_conversation_removes_messages(self):
        response = self.client.delete(
            f'/api/v1/conversations/{self.conversation.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')
        self.assertFalse(Conversation.objects.filter(id=self.conversation.id).exists())
        self.assertEqual(Message.objects.filter(conversation_id=self.conversation.id).count(), 0)

    def test_delete_other_users_conversation_returns_not_found(self):
        other_conversation = Conversation.objects.create(
            notebook=self.other_notebook,
            title='Not yours',
        )

        response = self.client.delete(
            f'/api/v1/conversations/{other_conversation.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Conversation.objects.filter(id=other_conversation.id).exists())


class BuildPromptTests(TestCase):
    def test_prompt_allows_general_questions_but_keeps_rag_guardrail(self):
        messages = build_prompt('你是什么模型', [])
        system = messages[0]['content']

        self.assertIn('通用问题，可以直接自然回答', system)
        self.assertIn('未检索到可用资料片段', messages[1]['content'])
        self.assertIn('资料片段：无', messages[1]['content'])

    def test_prompt_includes_web_results_with_web_source_numbers(self):
        messages = build_prompt(
            '联网搜索问题',
            [],
            web_results=[
                WebResult(
                    title='Web title',
                    url='https://example.com',
                    content='Web summary.',
                    position=1,
                )
            ],
        )

        self.assertIn('网页结果', messages[1]['content'])
        self.assertIn('[W1] 网页：Web title', messages[1]['content'])
        self.assertIn('https://example.com', messages[1]['content'])

    def test_prompt_marks_available_document_context_and_limits_image_claims(self):
        messages = build_prompt(
            '你读不了里面的图片吗',
            [
                Citation(
                    document_id=1,
                    document_name='report.docx',
                    chunk_id=10,
                    chunk_text='图 5-1 所示为系统流程图，步骤包括登录、上传、解析。',
                    position=3,
                    source_type='paragraph',
                    metadata={'source_type': 'paragraph'},
                )
            ],
        )

        self.assertIn('禁止说“没有读取到上传内容”', messages[0]['content'])
        self.assertIn('不能看见图片像素本身', messages[0]['content'])
        self.assertIn('资料状态：已检索到 Notebook 片段 1 个（正文段落 1 个）', messages[1]['content'])
        self.assertIn('chunk#3，正文段落', messages[1]['content'])

    def test_prompt_labels_heading_and_code_context(self):
        messages = build_prompt(
            '说明实现结构',
            [
                Citation(
                    document_id=1,
                    document_name='notes.md',
                    chunk_id=11,
                    chunk_text='系统设计',
                    position=0,
                    source_type='heading',
                    metadata={'source_type': 'heading', 'heading_level': 1},
                ),
                Citation(
                    document_id=1,
                    document_name='notes.md',
                    chunk_id=12,
                    chunk_text='print("ok")',
                    position=1,
                    source_type='code',
                    metadata={'source_type': 'code', 'language': 'python'},
                ),
            ],
        )

        self.assertIn('标题 1 个', messages[1]['content'])
        self.assertIn('代码块 1 个', messages[1]['content'])
        self.assertIn('chunk#0，标题', messages[1]['content'])
        self.assertIn('chunk#1，代码块', messages[1]['content'])

    def test_prompt_labels_image_ocr_context(self):
        messages = build_prompt(
            '图里写了什么',
            [
                Citation(
                    document_id=1,
                    document_name='report.md',
                    chunk_id=20,
                    chunk_text='[图片 OCR #1]\nOCR 文本：流程图包含上传、解析、检索。',
                    position=4,
                    source_type='image_ocr',
                    metadata={'source_type': 'image_ocr', 'asset_position': 0},
                )
            ],
        )

        self.assertIn('图片 OCR 1 个', messages[1]['content'])
        self.assertIn('chunk#4，图片 OCR', messages[1]['content'])

    def test_prompt_includes_recent_conversation_history(self):
        messages = build_prompt(
            '现在呢',
            [],
            history=[
                {'role': 'user', 'content': '我上传的文件你能读到吗'},
                {'role': 'assistant', 'content': '暂时不能。'},
            ],
        )

        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], '我上传的文件你能读到吗')
        self.assertEqual(messages[2]['role'], 'assistant')
        self.assertIn('用户问题：现在呢', messages[3]['content'])


class CitationPayloadTests(TestCase):
    def test_document_citation_payload_includes_source_metadata(self):
        payload = build_citation_payload(
            [
                Citation(
                    document_id=1,
                    document_name='report.docx',
                    chunk_id=2,
                    chunk_text='行 1: 模块 | 状态',
                    position=4,
                    source_type='table',
                    metadata={'source_type': 'table', 'table_index': 1},
                )
            ],
            [],
        )

        self.assertEqual(payload[0]['source_type'], 'document')
        self.assertEqual(payload[0]['document_source_type'], 'table')
        self.assertEqual(payload[0]['metadata']['table_index'], 1)


class RetrieveCitationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='rag-user',
            email='rag@example.com',
            password='test-password',
        )
        self.notebook = Notebook.objects.create(user=self.user, name='RAG notebook')
        self.document = Document.objects.create(
            notebook=self.notebook,
            name='report.docx',
            file_path='files/report.docx',
            file_type='docx',
            status=DocumentStatus.COMPLETED,
            chunk_count=2,
        )
        DocumentChunk.objects.create(
            document=self.document,
            content='项目背景和系统设计内容，包含需求分析、数据库设计和测试结果。',
            position=0,
            metadata={'source_type': 'paragraph'},
        )
        DocumentChunk.objects.create(
            document=self.document,
            content='本项目属于软件工程课程实践，主要实现笔记本资料管理和 AI 对话。',
            position=1,
            metadata={'source_type': 'paragraph'},
        )

    def test_chinese_sentence_query_matches_terms_inside_question(self):
        citations = retrieve_citations(
            self.notebook.id,
            '总结这个软件工程综合实验报告',
            top_k=2,
        )

        self.assertEqual(len(citations), 1)
        self.assertIn('软件工程课程实践', citations[0].chunk_text)

    def test_broad_summary_query_falls_back_to_document_context(self):
        citations = retrieve_citations(self.notebook.id, '总结一下这份报告', top_k=1)

        self.assertEqual(len(citations), 1)
        self.assertIn('项目背景', citations[0].chunk_text)

    def test_uploaded_file_query_falls_back_to_document_context(self):
        citations = retrieve_citations(self.notebook.id, '我上传的文件你能读到吗', top_k=1)

        self.assertEqual(len(citations), 1)
        self.assertIn('项目背景', citations[0].chunk_text)

    def test_specific_miss_does_not_return_unrelated_context(self):
        citations = retrieve_citations(self.notebook.id, '量子计算复杂度', top_k=1)

        self.assertEqual(citations, [])


class DeepSeekRetryTests(TestCase):
    @patch.dict('os.environ', {
        'DEEPSEEK_API_KEY': 'test-key',
        'DEEPSEEK_MODEL': 'deepseek-v4-flash',
        'DEEPSEEK_MAX_RETRIES': '1',
        'DEEPSEEK_RETRY_BACKOFF_SECONDS': '0',
    })
    @patch('apps.chat.rag.requests.post')
    def test_deepseek_retries_transient_network_error(self, post):
        post.side_effect = [
            request_exceptions.ChunkedEncodingError('ended early'),
            FakeResponse(
                payload={
                    'choices': [
                        {'message': {'content': 'retry success'}}
                    ]
                },
            ),
        ]

        result = call_deepseek_chat([{'role': 'user', 'content': 'hi'}])

        self.assertEqual(result, 'retry success')
        self.assertEqual(post.call_count, 2)

    @patch.dict('os.environ', {
        'DEEPSEEK_API_KEY': 'test-key',
        'DEEPSEEK_MODEL': 'deepseek-v4-flash',
        'DEEPSEEK_MAX_RETRIES': '2',
        'DEEPSEEK_RETRY_BACKOFF_SECONDS': '0',
    })
    @patch('apps.chat.rag.requests.post')
    def test_deepseek_auth_error_does_not_retry(self, post):
        post.return_value = FakeResponse(status_code=401, text='unauthorized')

        with self.assertRaises(DeepSeekAuthError):
            call_deepseek_chat([{'role': 'user', 'content': 'hi'}])

        self.assertEqual(post.call_count, 1)


class WebSearchRetryTests(TestCase):
    @patch.dict('os.environ', {
        'TAVILY_API_KEY': 'test-key',
        'TAVILY_MAX_RETRIES': '1',
        'TAVILY_RETRY_BACKOFF_SECONDS': '0',
    })
    @patch('apps.chat.web_search.requests.post')
    def test_tavily_retries_transient_network_error(self, post):
        post.side_effect = [
            request_exceptions.Timeout('timeout'),
            FakeResponse(
                payload={
                    'results': [
                        {
                            'title': 'Result',
                            'url': 'https://example.com',
                            'content': 'Summary',
                        }
                    ]
                },
            ),
        ]

        results = search_web('query')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'https://example.com')
        self.assertEqual(post.call_count, 2)

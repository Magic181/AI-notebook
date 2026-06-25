from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from requests import exceptions as request_exceptions
from rest_framework import status
from rest_framework.test import APIClient

from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .rag import DeepSeekAuthError, build_prompt, call_deepseek_chat
from .views import (
    AI_FAILURE_MESSAGE,
    WEB_ONLY_SEARCH_DEGRADED_MESSAGE,
    WEB_SEARCH_DEGRADED_MESSAGE,
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

    @patch('apps.chat.views.logger')
    @patch('apps.chat.views.call_deepseek_chat', side_effect=RuntimeError('service down'))
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

    @patch('apps.chat.views.search_web')
    @patch('apps.chat.views.retrieve_citations', return_value=[])
    @patch('apps.chat.views.call_deepseek_chat', return_value='这是联网搜索回答。')
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

    @patch('apps.chat.views.search_web')
    @patch('apps.chat.views.retrieve_citations', return_value=[])
    @patch('apps.chat.views.call_deepseek_chat', return_value='这是混合搜索回答。')
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

    @patch('apps.chat.views.search_web')
    @patch('apps.chat.views.retrieve_citations', return_value=[])
    @patch('apps.chat.views.call_deepseek_chat', return_value='兼容旧参数。')
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

    @patch('apps.chat.views.logger')
    @patch('apps.chat.views.search_web', side_effect=WebSearchError('search unavailable'))
    @patch('apps.chat.views.call_deepseek_chat', return_value='这是本地资料回答。')
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

    @patch('apps.chat.views.logger')
    @patch('apps.chat.views.search_web', side_effect=WebSearchError('search unavailable'))
    @patch('apps.chat.views.call_deepseek_chat', return_value='这是通用能力回答。')
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


class BuildPromptTests(TestCase):
    def test_prompt_allows_general_questions_but_keeps_rag_guardrail(self):
        messages = build_prompt('你是什么模型', [])
        system = messages[0]['content']

        self.assertIn('通用问题，可以直接自然回答', system)
        self.assertIn('资料型问题缺少足够资料', system)
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

        self.assertIn('网页搜索结果', messages[0]['content'])
        self.assertIn('[W1] 网页：Web title', messages[1]['content'])
        self.assertIn('https://example.com', messages[1]['content'])


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

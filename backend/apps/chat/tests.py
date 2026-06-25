from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .rag import build_prompt
from .views import AI_FAILURE_MESSAGE
from .web_search import WebResult


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
    @patch('apps.chat.views.call_deepseek_chat', return_value='这是联网搜索回答。')
    def test_send_message_with_web_search_saves_web_sources(
        self,
        _,
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
            {'content': '搜索最新资料', 'web_search': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        search_web.assert_called_once_with('搜索最新资料')

        assistant = Message.objects.filter(role=MessageRole.ASSISTANT).latest('id')
        self.assertEqual(assistant.content, '这是联网搜索回答。')
        self.assertEqual(assistant.citations[0]['source_type'], 'web')
        self.assertEqual(assistant.citations[0]['url'], 'https://example.com/article')


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

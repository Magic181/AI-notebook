from django.urls import path

from . import views

urlpatterns = [
    path(
        "notebooks/<int:notebook_pk>/conversations/",
        views.NotebookConversationListCreateView.as_view(),
        name="notebook-conversations",
    ),
    path(
        "conversations/<int:conversation_pk>/messages/",
        views.ConversationMessageListView.as_view(),
        name="conversation-messages",
    ),
    path(
        "conversations/<int:conversation_pk>/",
        views.ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
    path(
        "conversations/<int:conversation_pk>/messages/send/",
        views.ConversationSendMessageView.as_view(),
        name="conversation-send",
    ),
]


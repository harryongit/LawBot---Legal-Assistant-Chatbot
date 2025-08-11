from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import chat_view, chat_api, messages_api, MessageViewSet, api_docs_view

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path("", chat_view, name="chat"),
    path("api/docs/", api_docs_view, name="api_docs"),
    path("api/chat/", chat_api, name="chat_api"),
    path("api/messages/", messages_api, name="messages_api"),
    path("api/", include(router.urls)),  # This includes all ViewSet endpoints
]

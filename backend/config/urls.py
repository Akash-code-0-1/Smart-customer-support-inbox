from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import ConversationListView, ConversationDetailView, AISuggestionView
from core.sse import conversation_stream

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('api/conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('api/conversations/<int:pk>/suggest-reply/', AISuggestionView.as_view(), name='ai-suggestion'),
    path('api/conversations/<int:pk>/stream/', conversation_stream, name='conversation-stream'),
]
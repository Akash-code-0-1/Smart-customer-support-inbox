# backend/config/urls.py
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import ConversationListView, ConversationDetailView, AISuggestionView
from core.sse import conversation_stream


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/conversations/', ConversationListView.as_view(), name='conversation-list'),
    
    # xplicit sub-resource ST
    path('api/conversations/<int:pk>/suggest-reply/', AISuggestionView.as_view(), name='ai-suggestion'),
    path("api/conversations/<int:pk>/stream/", conversation_stream, name="conversation-stream"),
    
    # Generic variable-capture detail route
    path('api/conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),

    # OpenAPI Documentation Schemas
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
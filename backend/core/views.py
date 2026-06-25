from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .tasks import analyze_sentiment_task

LOCK_EXPIRY = 300  # 5 minutes

class StandardPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Conversation.objects.all()
        status_param = self.request.query_params.get("status")
        search_param = self.request.query_params.get("search")
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if search_param:
            queryset = queryset.filter(customer_name__icontains=search_param)
        return queryset

class ConversationDetailView(APIView):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        current_lock_user = cache.get(lock_key)
        
        if current_lock_user is None:
            cache.set(lock_key, request.user.email, timeout=LOCK_EXPIRY)
            current_lock_user = request.user.email
            cache.set(f"sse:channel:{pk}", [{"type": "lock_update", "data": {"lock_holder": current_lock_user}}], timeout=60)
        elif current_lock_user == request.user.email:
            cache.touch(lock_key, timeout=LOCK_EXPIRY)
            
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            "lock_holder": current_lock_user,
            "is_locked_by_me": current_lock_user == request.user.email,
            "messages": serializer.data
        })

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        lock_holder = cache.get(lock_key)

        if lock_holder and lock_holder != request.user.email:
            return Response(
                {"error": f"Thread is locked by agent {lock_holder}"}, 
                status=status.HTTP_423_LOCKED
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                message_obj = serializer.save(conversation=conversation, sender="agent")
                conversation.save()
            
            analyze_sentiment_task.delay(message_obj.id)
            
            # Append real-time stream broadcast events
            channel_key = f"sse:channel:{pk}"
            events = cache.get(channel_key, [])
            events.append({"type": "message", "data": serializer.data})
            cache.set(channel_key, events, timeout=60)
            
            cache.set(lock_key, request.user.email, timeout=LOCK_EXPIRY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AISuggestionView(APIView):
    def post(self, request, pk):
        message_text = request.data.get("message", "").lower()
        if "refund" in message_text:
            suggestion = "We are truly sorry to hear that you want a refund. I can assist you with processing that immediately if your order falls within our 30-day window."
        elif "broken" in message_text or "damaged" in message_text:
            suggestion = "I apologize for the damaged item. Could you please upload a clear picture so I can dispatch a replacement unit right away?"
        elif "delay" in message_text or "where is my order" in message_text:
            suggestion = "Let me look up your tracking sequence. Please provide your Order Confirmation Number so I can locate your parcel."
        else:
            suggestion = "Thank you for contacting customer support. How can I assist you with your inquiries today?"
            
        return Response({"suggestion": suggestion}, status=status.HTTP_200_OK)
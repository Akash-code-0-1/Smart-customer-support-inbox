from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .pagination import StandardPagination
from .tasks import analyze_sentiment_task

LOCK_EXPIRY = 300  # 5 Minutes in seconds

class ConversationListView(generics.ListAPIView):
    """
    Exposes paginated ticket queues with case-insensitive search 
    and direct relational key filtering capabilities.
    """
    serializer_class = ConversationSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Conversation.objects.all().order_by('-updated_at')
        status_param = self.request.query_params.get("status")
        search_param = self.request.query_params.get("search")
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if search_param:
            queryset = queryset.filter(customer_name__icontains=search_param)
            
        return queryset


class ConversationDetailView(APIView):
    """
    Manages state concurrency allocation locking, historical thread records,
    and handles dynamic incoming multi-sender payload ingest streams.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        current_lock_user = cache.get(lock_key)
        user_email = request.user.email
        
        # Concurrency Allocation Lock Logic
        if current_lock_user is None:
            cache.set(lock_key, user_email, timeout=LOCK_EXPIRY)
            current_lock_user = user_email
        elif current_lock_user == user_email:
            cache.touch(lock_key, timeout=LOCK_EXPIRY)
            
        messages = conversation.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            "lock_holder": current_lock_user,
            "is_locked_by_me": current_lock_user == user_email,
            "sentiment": conversation.sentiment,  # ✨ Senior Fix: Returns the live data context to Next.js
            "messages": serializer.data
        })

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        current_lock_user = cache.get(lock_key)
        
        # Extract sender from payload; default cleanly to agent if absent
        request_sender = request.data.get("sender", "agent")
        
        # Senior Validation: Block unauthorized agents, but bypass for customer simulation inputs
        if request_sender != "customer" and current_lock_user and current_lock_user != request.user.email:
            return Response(
                {"error": f"Thread write locked by agent: {current_lock_user}"}, 
                status=status.HTTP_423_LOCKED
            )
            
        # Support both 'text' and 'message' property lookups flexibly
        payload_data = request.data.copy()
        if "text" not in payload_data and "message" in payload_data:
            payload_data["text"] = payload_data["message"]
            
        serializer = MessageSerializer(data=payload_data)
        if serializer.is_valid():
            # Dynamically apply sender designation context instead of a hardcoded string
            message_obj = serializer.save(
                conversation=conversation, 
                sender=request_sender
            )
            
            # Re-serialize model layout instance to catch auto-generated fields (id, created_at)
            fresh_serialized_data = MessageSerializer(message_obj).data
            
            # 1. Pipeline background sentiment analysis job assignment to Celery
            analyze_sentiment_task.delay(message_obj.id)
            
            # 2. Append payload out to the live Server-Sent Events (SSE) channel queue buffer
            channel_key = f"sse:channel:{pk}"
            events = cache.get(channel_key, [])
            events.append({"type": "message", "data": fresh_serialized_data})
            cache.set(channel_key, events, timeout=60)
            
            return Response(fresh_serialized_data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AISuggestionView(APIView):
    """
    Exposes static rules token matrix matching to provide algorithmic recommendation macros.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Handle field variance gracefully across incoming payload schemas
        raw_text = request.data.get("message") or request.data.get("text") or ""
        message_text = raw_text.lower()
        
        if any(w in message_text for w in ["hi", "hello", "hey", "greetings"]):
            suggestion = "Hello! Thank you for contacting customer support. How can I assist you with your account or order today?"
            
        elif any(w in message_text for w in ["refund", "money back", "chargeback", "return"]):
            suggestion = "We are sorry to hear that you are unsatisfied. I can process a full refund for your order immediately under our 30-day guarantee policy."
            
        elif any(w in message_text for w in ["broken", "damaged", "faulty", "cracked", "defective"]):
            suggestion = "I apologize for the delivery condition. Let me arrange a priority replacement package shipment to your address free of charge right away."
            
        elif any(w in message_text for w in ["track", "shipment", "where is my", "delivery", "status"]):
            suggestion = "I would be happy to check your shipping tracking parameters. Could you please provide your order identifier details?"
            
        elif any(w in message_text for w in ["login", "password", "account", "access", "reset"]):
            suggestion = "For security purposes, I have dispatched a secure password reset validation link directly to your registered email address."
            
        elif any(w in message_text for w in ["cancel", "close", "terminate", "stop"]):
            suggestion = "I'm sad to see you go. I can help cancel your subscription immediately. Please confirm if you want me to proceed."
            
        else:
            suggestion = "Thank you for bringing this to our attention. Let me check our account records to help resolve this case as quickly as possible."
            
        return Response({"suggestion": suggestion}, status=status.HTTP_200_OK)
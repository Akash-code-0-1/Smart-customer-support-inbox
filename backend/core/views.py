# from django.core.cache import cache
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from .models import Conversation, Message
# from .serializers import ConversationSerializer, MessageSerializer
# from .tasks import analyze_sentiment_task
# from rest_framework.permissions import AllowAny

# LOCK_EXPIRY = 300  # 5 minutes

# class StandardPagination(PageNumberPagination):
#     page_size = 15
#     page_size_query_param = "page_size"

# class ConversationListView(generics.ListAPIView):
#     serializer_class = ConversationSerializer
#     pagination_class = StandardPagination
#     permission_classes = [AllowAny]  # <-- Add this explicit line
    
#     def get_queryset(self):
#         queryset = Conversation.objects.all()
#         status_param = self.request.query_params.get("status")
#         search_param = self.request.query_params.get("search")
#         if status_param:
#             queryset = queryset.filter(status=status_param)
#         if search_param:
#             queryset = queryset.filter(customer_name__icontains=search_param)
#         return queryset

# class ConversationDetailView(APIView):
#     permission_classes = [AllowAny]  # <-- Add this explicit line

#     def get(self, request, pk):
#         conversation = get_object_or_404(Conversation, pk=pk)
#         messages = conversation.messages.all()
#         serializer = MessageSerializer(messages, many=True)
        
#         return Response({
#             "lock_holder": "admin@test.com",
#             "is_locked_by_me": True,
#             "messages": serializer.data
#         })

#     def post(self, request, pk):
#         conversation = get_object_or_404(Conversation, pk=pk)
#         serializer = MessageSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save message objects with standard fallback agent context mapping
#             serializer.save(conversation=conversation, sender="agent")
            
#             # Real-time event simulation trigger
#             channel_key = f"sse:channel:{pk}"
#             events = cache.get(channel_key, [])
#             events.append({"type": "message", "data": serializer.data})
#             cache.set(channel_key, events, timeout=60)
            
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AISuggestionView(APIView):
#     def post(self, request, pk):
#         message_text = request.data.get("message", "").lower()
#         if "refund" in message_text:
#             suggestion = "We are truly sorry to hear that you want a refund. I can assist you with processing that immediately if your order falls within our 30-day window."
#         elif "broken" in message_text or "damaged" in message_text:
#             suggestion = "I apologize for the damaged item. Could you please upload a clear picture so I can dispatch a replacement unit right away?"
#         elif "delay" in message_text or "where is my order" in message_text:
#             suggestion = "Let me look up your tracking sequence. Please provide your Order Confirmation Number so I can locate your parcel."
#         else:
#             suggestion = "Thank you for contacting customer support. How can I assist you with your inquiries today?"
            
#         return Response({"suggestion": suggestion}, status=status.HTTP_200_OK)


# backend/core/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .pagination import StandardPagination
from .tasks import analyze_sentiment_task

LOCK_EXPIRY = 300  # 5 Minutes in seconds

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        current_lock_user = cache.get(lock_key)
        user_email = request.user.email
        
        # Concurrency Lock Logic
        if current_lock_user is None:
            cache.set(lock_key, user_email, timeout=LOCK_EXPIRY)
            current_lock_user = user_email
        elif current_lock_user == user_email:
            cache.touch(lock_key, timeout=LOCK_EXPIRY)
            
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            "lock_holder": current_lock_user,
            "is_locked_by_me": current_lock_user == user_email,
            "messages": serializer.data
        })

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        lock_key = f"lock:conversation:{pk}"
        current_lock_user = cache.get(lock_key)
        
        # Block unauthorized agent mutation modifications
        if current_lock_user and current_lock_user != request.user.email:
            return Response({"error": f"Thread write locked by agent: {current_lock_user}"}, status=status.HTTP_423_LOCKED)
            
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message_obj = serializer.save(conversation=conversation, sender="agent")
            
            # 1. Trigger background job processing task for Sentiment Analysis
            analyze_sentiment_task.delay(message_obj.id)
            
            # 2. Push message to real-time SSE event buffer channel
            channel_key = f"sse:channel:{pk}"
            events = cache.get(channel_key, [])
            events.append({"type": "message", "data": serializer.data})
            cache.set(channel_key, events, timeout=60)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AISuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    # Indented by 4 spaces to live inside the class block context
    def post(self, request, pk):
        message_text = request.data.get("message", "").lower()
        
        # --- Senior Level Expanded Keyword Matrix ---
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
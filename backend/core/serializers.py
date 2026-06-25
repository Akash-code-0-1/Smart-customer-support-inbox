from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.CharField(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'customer_name', 'last_message', 'status', 'sentiment', 'created_at']
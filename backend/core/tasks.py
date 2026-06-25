from celery import shared_task
from .models import Message, Conversation

@shared_task
def analyze_sentiment_task(message_id):
    try:
        msg = Message.objects.get(id=message_id)
        text = msg.message.lower()
        conversation = msg.conversation
        
        # Rule matrix evaluation algorithm logic
        if any(w in text for w in ["terrible", "broken", "refund", "bad", "worst"]):
            conversation.sentiment = "negative"
        elif any(w in text for w in ["great", "awesome", "perfect", "thanks", "love"]):
            conversation.sentiment = "positive"
        else:
            conversation.sentiment = "neutral"
            
        conversation.save()
        return f"Sentiment evaluated successfully for message {message_id}: {conversation.sentiment}"
    except Message.DoesNotExist:
        return f"Message ID {message_id} vanished before task compilation."
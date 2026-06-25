from celery import shared_task
from .models import Message, Conversation, SentimentScore

@shared_task
def analyze_sentiment_task(message_id):
    try:
        msg = Message.objects.get(id=message_id)
        text = msg.message.lower()
        
        positive_keywords = ["love", "great", "awesome", "perfect", "thanks", "thank you", "solved"]
        negative_keywords = ["bad", "broken", "terrible", "worst", "refund", "angry", "defect", "fail"]
        
        pos_count = sum(1 for word in positive_keywords if word in text)
        neg_count = sum(1 for word in negative_keywords if word in text)
        
        if neg_count > pos_count:
            score = SentimentScore.NEGATIVE
        elif pos_count > neg_count:
            score = SentimentScore.POSITIVE
        else:
            score = SentimentScore.NEUTRAL
            
        conversation = msg.conversation
        conversation.sentiment = score
        conversation.save(update_fields=["sentiment"])
        return f"Conversation {conversation.id} sentiment set to {score}"
    except Message.DoesNotExist:
        return "Message records not discovered"
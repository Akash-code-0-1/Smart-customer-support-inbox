from django.db import models

class ConversationStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    PENDING = "pending", "Pending"

class SentimentScore(models.TextChoices):
    POSITIVE = "Positive", "Positive"
    NEUTRAL = "Neutral", "Neutral"
    NEGATIVE = "Negative", "Negative"
    UNPROCESSED = "Unprocessed", "Unprocessed"

class Conversation(models.Model):
    customer_name = models.CharField(max_length=255, db_index=True)
    status = models.CharField(
        max_length=10, 
        choices=ConversationStatus.choices, 
        default=ConversationStatus.OPEN,
        db_index=True
    )
    sentiment = models.CharField(
        max_length=15,
        choices=SentimentScore.choices,
        default=SentimentScore.UNPROCESSED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    @property
    def last_message(self):
        msg = self.messages.last()
        return msg.message if msg else ""

class Message(models.Model):
    class SenderChoices(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AGENT = "agent", "Agent"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SenderChoices.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
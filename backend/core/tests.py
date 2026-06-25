from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message, SentimentScore
from .tasks import analyze_sentiment_task

class BackendComprehensiveTestSuite(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="admin@test.com", 
            email="admin@test.com", 
            password="admin123"
        )
        self.conversation = Conversation.objects.create(customer_name="John Doe", status="open")
        
        # Authenticate the test client
        response = self.client.post('/api/token/', {'username': 'admin@test.com', 'password': 'admin123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_jwt_authentication_flow(self):
        self.client.credentials()  # Wipe credentials
        res = self.client.get(reverse('conversation-list'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_paginated_thread_retrieval(self):
        res = self.client.get(reverse('conversation-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)

    def test_locking_state_collision(self):
        # Establish base lock context for the admin user via GET
        self.client.get(reverse('conversation-detail', kwargs={'pk': self.conversation.id}))
        
        # Simulate lock overwrite belonging to another agent
        cache.set(f"lock:conversation:{self.conversation.id}", "agent2@test.com", timeout=300)
        
        payload = {"message": "Violating concurrent lock system safeguards"}
        res = self.client.post(reverse('conversation-detail', kwargs={'pk': self.conversation.id}), payload)
        self.assertEqual(res.status_code, status.HTTP_423_LOCKED)

    def test_celery_sentiment_analyzer_task(self):
        msg = Message.objects.create(
            conversation=self.conversation, 
            sender="customer", 
            message="This service is terrible and broken"
        )
        analyze_sentiment_task(msg.id)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.sentiment, SentimentScore.NEGATIVE)
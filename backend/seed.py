import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Conversation, Message

def seed():
    if not User.objects.filter(username="admin@test.com").exists():
        User.objects.create_superuser(
            username="admin@test.com",
            email="admin@test.com",
            password="admin123"
        )
        print("Evaluation Admin Account Root Seed Created.")
        
    
    c, _ = Conversation.objects.get_or_create(customer_name="John Doe", status="open")
    Message.objects.get_or_create(conversation=c, sender="customer", message="Need help with a product refund.")
    print("Core Stub Models Seeding Phase Confirmed.")

if __name__ == '__main__':
    seed()
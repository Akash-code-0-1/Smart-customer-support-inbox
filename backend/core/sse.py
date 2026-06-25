import time
import json
from django.http import StreamingHttpResponse
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_stream(request, pk):
    def event_stream():
        cache_key = f"sse:channel:{pk}"
        cache.set(cache_key, [], timeout=60)
        
        while True:
            events = cache.get(cache_key, [])
            if events:
                for event in events:
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                cache.set(cache_key, [], timeout=60)
            time.sleep(1)
            
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
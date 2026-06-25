# backend/core/sse.py
import time
import json
from django.http import StreamingHttpResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def conversation_stream(request, pk):
    def event_stream():
        cache_key = f"sse:channel:{pk}"
        # Send an immediate connection confirmation chunk
        yield f"data: {json.dumps({'status': 'connected'})}\n\n"
        
        while True:
            events = cache.get(cache_key, [])
            if events:
                for event in events:
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                cache.set(cache_key, [], timeout=60)
            time.sleep(1)
            
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache, must-revalidate"
    response["X-Accel-Buffering"] = "no"
    # Explicitly allow cross-origin requests for local frontend support
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"
    return response
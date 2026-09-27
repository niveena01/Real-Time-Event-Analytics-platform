import pytest
import json
import redis
from app.workers.tasks import process_event_batch
from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def test_process_event_batch_empty():
    redis_client.delete("raw_events_queue")
    result = process_event_batch()
    assert result == "No events in queue"
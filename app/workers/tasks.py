from app.workers.celery_app import celery_app
from app.config import settings
import redis
import json
import psycopg2
from psycopg2.extras import execute_values

redis_client = redis.Redis.from_url(settings.REDIS_URL)

@celery_app.task(name="app.workers.tasks.process_event_batch")
def process_event_batch():
    pipe = redis_client.pipeline()
    pipe.lrange("raw_events_queue", 0, 999)
    pipe.ltrim("raw_events_queue", 1000, -1)
    results = pipe.execute()
    
    raw_batch = results[0]
    if not raw_batch:
        return "No events in queue"

    events = [json.loads(item.decode("utf-8")) for item in raw_batch]
    
    # Anomaly scanning logic
    error_count = sum(1 for e in events if e.get("event_type") == "error_500")
    if len(events) > 0 and (error_count / len(events)) > 0.05:
        alert_payload = json.dumps({
            "type": "ANOMALY_DETECTED",
            "message": f"High error spike detected: {error_count} error events in batch of {len(events)}",
            "error_rate": f"{(error_count/len(events))*100:.2f}%"
        })
        redis_client.publish("anomalies_channel", alert_payload)

    # Bulk DB Insert Execution
    try:
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO events (client_id, event_type, latency_ms, metadata_json)
            VALUES %s
        """
        records = [
            (e["client_id"], e["event_type"], e["latency_ms"], json.dumps(e.get("metadata")))
            for e in events
        ]
        
        execute_values(cursor, insert_query, records)
        conn.commit()
        cursor.close()
        conn.close()
        return f"Successfully batch inserted {len(events)} events"
    except Exception as e:
        return f"Batch insertion failed: {str(e)}"
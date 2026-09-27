CREATE TABLE IF NOT EXISTS events (
    id SERIAL,
    client_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    latency_ms INT NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    metadata_json JSONB
);

SELECT create_hypertable('events', 'timestamp', if_not_exists => TRUE);
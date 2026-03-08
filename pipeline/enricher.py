from datetime import datetime, timezone


# Enrichment maps — add context to raw alert events
SOURCE_LABELS = {
    'cloud-telemetry-agent': 'Infrastructure Monitoring',
    'synthetic-uptime-monitor': 'Uptime Monitoring',
    'log-intelligence-engine': 'Log Intelligence',
    'manual': 'Manual Entry'
}

ALERT_TYPE_LABELS = {
    'THRESHOLD_BREACH': 'Metric Threshold Breach',
    'ENDPOINT_DOWN': 'Endpoint Unavailable',
    'SLOW_RESPONSE': 'Slow Response Detected',
    'HEALTH_DEGRADED': 'System Health Degraded',
    'LOG_ANOMALY': 'Log Anomaly Detected'
}


def enrich_event(event):
    """
    Enriches a raw alert event with human-readable labels,
    environment context, and operational metadata.
    """
    enriched = event.copy()

    # Add human-readable labels
    enriched['source_label'] = SOURCE_LABELS.get(
        event['source'], event['source']
    )
    enriched['alert_type_label'] = ALERT_TYPE_LABELS.get(
        event['alert_type'], event['alert_type']
    )

    # Add environment context
    enriched['environment'] = 'production'
    enriched['enriched_at'] = datetime.now(timezone.utc).isoformat()

    # Add operational tags
    tags = []
    if 'cpu' in event['message'].lower():
        tags.append('compute')
    if 'memory' in event['message'].lower():
        tags.append('memory')
    if 'disk' in event['message'].lower():
        tags.append('storage')
    if 'endpoint' in event['message'].lower() or 'url' in str(event['metadata']):
        tags.append('network')
    if 'log' in event['message'].lower():
        tags.append('logging')

    enriched['tags'] = tags

    return enriched


def enrich_all(events):
    return [enrich_event(event) for event in events]

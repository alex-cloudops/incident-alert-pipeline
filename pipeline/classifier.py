def classify_event(event):
    """
    Classifies enriched alert events by severity and urgency.
    Severity drives routing decisions downstream.
    """
    classified = event.copy()
    severity = 'LOW'
    urgency = 'ROUTINE'

    source = event.get('source', '')
    alert_type = event.get('alert_type', '')
    message = event.get('message', '').lower()
    metadata = event.get('metadata', {})

    # CRITICAL conditions
    if alert_type == 'ENDPOINT_DOWN':
        severity = 'CRITICAL'
        urgency = 'IMMEDIATE'

    elif alert_type == 'THRESHOLD_BREACH':
        value = metadata.get('value', 0)
        metric = metadata.get('metric', '')

        if metric == 'cpu_percent' and value >= 95:
            severity = 'CRITICAL'
            urgency = 'IMMEDIATE'
        elif metric == 'cpu_percent' and value >= 85:
            severity = 'HIGH'
            urgency = 'PROMPT'
        elif metric == 'memory_percent' and value >= 95:
            severity = 'CRITICAL'
            urgency = 'IMMEDIATE'
        elif metric == 'memory_percent' and value >= 90:
            severity = 'HIGH'
            urgency = 'PROMPT'
        elif metric == 'disk_percent' and value >= 95:
            severity = 'CRITICAL'
            urgency = 'IMMEDIATE'
        elif metric == 'disk_percent' and value >= 90:
            severity = 'HIGH'
            urgency = 'PROMPT'

    elif alert_type == 'HEALTH_DEGRADED':
        error_rate = metadata.get('error_rate', 0)
        if error_rate >= 15:
            severity = 'CRITICAL'
            urgency = 'IMMEDIATE'
        elif error_rate >= 10:
            severity = 'HIGH'
            urgency = 'PROMPT'
        else:
            severity = 'MEDIUM'
            urgency = 'ROUTINE'

    elif alert_type == 'SLOW_RESPONSE':
        response_time = metadata.get('response_time_ms', 0)
        if response_time >= 5000:
            severity = 'HIGH'
            urgency = 'PROMPT'
        else:
            severity = 'MEDIUM'
            urgency = 'ROUTINE'

    elif alert_type == 'LOG_ANOMALY':
        severity = 'MEDIUM'
        urgency = 'ROUTINE'

    classified['severity'] = severity
    classified['urgency'] = urgency

    return classified


def classify_all(events):
    return [classify_event(event) for event in events]
import json
import uuid
from datetime import datetime, timezone


def create_event(source, alert_type, message, metadata=None):
    """
    Creates a standardized alert event from any source.
    This is the pipeline entry point — all alerts get normalized here.
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'source': source,
        'alert_type': alert_type,
        'message': message,
        'metadata': metadata or {},
        'received_at': datetime.now(timezone.utc).isoformat(),
        'status': 'NEW'
    }
    return event


def load_sample_events():
    """
    Simulated incoming alert events from across the portfolio ecosystem.
    In production these would arrive via API, queue, or webhook.
    """
    return [
        create_event(
            source='cloud-telemetry-agent',
            alert_type='THRESHOLD_BREACH',
            message='memory_percent is at 91.0% on my-server-01',
            metadata={'metric': 'memory_percent', 'value': 91.0, 'threshold': 90.0}
        ),
        create_event(
            source='synthetic-uptime-monitor',
            alert_type='ENDPOINT_DOWN',
            message='HTTPBin Simulated Failure is DOWN — status code 503',
            metadata={'url': 'https://httpbin.org/status/503', 'status_code': 503}
        ),
        create_event(
            source='cloud-telemetry-agent',
            alert_type='THRESHOLD_BREACH',
            message='cpu_percent is at 97.0% on prod-server-02',
            metadata={'metric': 'cpu_percent', 'value': 97.0, 'threshold': 85.0}
        ),
        create_event(
            source='log-intelligence-engine',
            alert_type='HEALTH_DEGRADED',
            message='Log analysis detected CRITICAL health status on app-server.log',
            metadata={'file': 'app-server.log', 'error_rate': 15.3}
        ),
        create_event(
            source='synthetic-uptime-monitor',
            alert_type='SLOW_RESPONSE',
            message='GitHub response time of 3200ms exceeds threshold of 2000ms',
            metadata={'url': 'https://www.github.com', 'response_time_ms': 3200}
        )
    ]
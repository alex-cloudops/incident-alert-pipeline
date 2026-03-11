import pytest
from pipeline.classifier import classify_event, classify_all


def make_event(alert_type, source='cloud-telemetry-agent', message='test alert', metadata=None):
    """Helper — build a raw alert event with controlled values."""
    return {
        'source': source,
        'alert_type': alert_type,
        'message': message,
        'metadata': metadata or {}
    }


class TestEndpointDown:
    def test_endpoint_down_classifies_as_critical(self):
        event = make_event('ENDPOINT_DOWN')
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_endpoint_down_urgency_is_immediate(self):
        event = make_event('ENDPOINT_DOWN')
        result = classify_event(event)
        assert result['urgency'] == 'IMMEDIATE'


class TestThresholdBreachCpu:
    def test_cpu_at_95_is_critical(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 95})
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_cpu_above_95_is_critical(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 97})
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_cpu_at_85_is_high(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 85})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'

    def test_cpu_just_below_critical_is_high(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 94})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'

    def test_cpu_critical_urgency_is_immediate(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 95})
        result = classify_event(event)
        assert result['urgency'] == 'IMMEDIATE'

    def test_cpu_high_urgency_is_prompt(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'cpu_percent', 'value': 85})
        result = classify_event(event)
        assert result['urgency'] == 'PROMPT'


class TestThresholdBreachMemory:
    def test_memory_at_95_is_critical(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'memory_percent', 'value': 95})
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_memory_at_90_is_high(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'memory_percent', 'value': 90})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'

    def test_memory_just_below_critical_is_high(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'memory_percent', 'value': 94})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'


class TestThresholdBreachDisk:
    def test_disk_at_95_is_critical(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'disk_percent', 'value': 95})
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_disk_at_90_is_high(self):
        event = make_event('THRESHOLD_BREACH', metadata={'metric': 'disk_percent', 'value': 90})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'


class TestHealthDegraded:
    def test_error_rate_at_15_is_critical(self):
        event = make_event('HEALTH_DEGRADED', metadata={'error_rate': 15})
        result = classify_event(event)
        assert result['severity'] == 'CRITICAL'

    def test_error_rate_at_10_is_high(self):
        event = make_event('HEALTH_DEGRADED', metadata={'error_rate': 10})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'

    def test_error_rate_below_10_is_medium(self):
        event = make_event('HEALTH_DEGRADED', metadata={'error_rate': 5})
        result = classify_event(event)
        assert result['severity'] == 'MEDIUM'


class TestSlowResponse:
    def test_response_at_5000ms_is_high(self):
        event = make_event('SLOW_RESPONSE', metadata={'response_time_ms': 5000})
        result = classify_event(event)
        assert result['severity'] == 'HIGH'

    def test_response_below_5000ms_is_medium(self):
        event = make_event('SLOW_RESPONSE', metadata={'response_time_ms': 3200})
        result = classify_event(event)
        assert result['severity'] == 'MEDIUM'

    def test_slow_response_high_urgency_is_prompt(self):
        event = make_event('SLOW_RESPONSE', metadata={'response_time_ms': 5000})
        result = classify_event(event)
        assert result['urgency'] == 'PROMPT'

    def test_slow_response_medium_urgency_is_routine(self):
        event = make_event('SLOW_RESPONSE', metadata={'response_time_ms': 3200})
        result = classify_event(event)
        assert result['urgency'] == 'ROUTINE'


class TestLogAnomaly:
    def test_log_anomaly_is_medium(self):
        event = make_event('LOG_ANOMALY')
        result = classify_event(event)
        assert result['severity'] == 'MEDIUM'

    def test_log_anomaly_urgency_is_routine(self):
        event = make_event('LOG_ANOMALY')
        result = classify_event(event)
        assert result['urgency'] == 'ROUTINE'


class TestUnknownAlertType:
    def test_unknown_alert_type_defaults_to_low(self):
        event = make_event('UNKNOWN_TYPE')
        result = classify_event(event)
        assert result['severity'] == 'LOW'

    def test_unknown_alert_type_defaults_to_routine(self):
        event = make_event('UNKNOWN_TYPE')
        result = classify_event(event)
        assert result['urgency'] == 'ROUTINE'


class TestClassifyAll:
    def test_classify_all_processes_every_event(self):
        events = [
            make_event('ENDPOINT_DOWN'),
            make_event('LOG_ANOMALY'),
            make_event('SLOW_RESPONSE', metadata={'response_time_ms': 3000})
        ]
        results = classify_all(events)
        assert len(results) == 3

    def test_classify_all_adds_severity_to_each_event(self):
        events = [make_event('ENDPOINT_DOWN'), make_event('LOG_ANOMALY')]
        results = classify_all(events)
        for result in results:
            assert 'severity' in result
            assert 'urgency' in result
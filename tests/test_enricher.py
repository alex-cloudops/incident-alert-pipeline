import pytest
from pipeline.enricher import enrich_event, enrich_all


def make_event(source='cloud-telemetry-agent', alert_type='THRESHOLD_BREACH', message='test alert', metadata=None):
    """Helper — build a raw alert event with controlled values."""
    return {
        'source': source,
        'alert_type': alert_type,
        'message': message,
        'metadata': metadata or {}
    }


class TestSourceLabels:
    def test_telemetry_agent_gets_correct_label(self):
        event = make_event(source='cloud-telemetry-agent')
        result = enrich_event(event)
        assert result['source_label'] == 'Infrastructure Monitoring'

    def test_uptime_monitor_gets_correct_label(self):
        event = make_event(source='synthetic-uptime-monitor')
        result = enrich_event(event)
        assert result['source_label'] == 'Uptime Monitoring'

    def test_log_engine_gets_correct_label(self):
        event = make_event(source='log-intelligence-engine')
        result = enrich_event(event)
        assert result['source_label'] == 'Log Intelligence'

    def test_unknown_source_falls_back_to_source_value(self):
        event = make_event(source='unknown-source')
        result = enrich_event(event)
        assert result['source_label'] == 'unknown-source'


class TestAlertTypeLabels:
    def test_threshold_breach_gets_correct_label(self):
        event = make_event(alert_type='THRESHOLD_BREACH')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'Metric Threshold Breach'

    def test_endpoint_down_gets_correct_label(self):
        event = make_event(alert_type='ENDPOINT_DOWN')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'Endpoint Unavailable'

    def test_slow_response_gets_correct_label(self):
        event = make_event(alert_type='SLOW_RESPONSE')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'Slow Response Detected'

    def test_health_degraded_gets_correct_label(self):
        event = make_event(alert_type='HEALTH_DEGRADED')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'System Health Degraded'

    def test_log_anomaly_gets_correct_label(self):
        event = make_event(alert_type='LOG_ANOMALY')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'Log Anomaly Detected'

    def test_unknown_alert_type_falls_back_to_alert_type_value(self):
        event = make_event(alert_type='UNKNOWN_TYPE')
        result = enrich_event(event)
        assert result['alert_type_label'] == 'UNKNOWN_TYPE'


class TestEnvironmentAndTimestamp:
    def test_environment_is_set_to_production(self):
        event = make_event()
        result = enrich_event(event)
        assert result['environment'] == 'production'

    def test_enriched_at_timestamp_is_added(self):
        event = make_event()
        result = enrich_event(event)
        assert 'enriched_at' in result
        assert result['enriched_at'] is not None


class TestTagGeneration:
    def test_cpu_message_gets_compute_tag(self):
        event = make_event(message='cpu_percent is at 97% on server-01')
        result = enrich_event(event)
        assert 'compute' in result['tags']

    def test_memory_message_gets_memory_tag(self):
        event = make_event(message='memory_percent is at 91% on server-01')
        result = enrich_event(event)
        assert 'memory' in result['tags']

    def test_disk_message_gets_storage_tag(self):
        event = make_event(message='disk usage critical on server-01')
        result = enrich_event(event)
        assert 'storage' in result['tags']

    def test_log_message_gets_logging_tag(self):
        event = make_event(message='log analysis detected anomaly')
        result = enrich_event(event)
        assert 'logging' in result['tags']

    def test_unrelated_message_gets_empty_tags(self):
        event = make_event(message='generic alert with no keywords')
        result = enrich_event(event)
        assert result['tags'] == []

    def test_multiple_keywords_get_multiple_tags(self):
        event = make_event(message='cpu and memory both critical')
        result = enrich_event(event)
        assert 'compute' in result['tags']
        assert 'memory' in result['tags']


class TestOriginalFieldsPreserved:
    def test_source_is_preserved(self):
        event = make_event(source='cloud-telemetry-agent')
        result = enrich_event(event)
        assert result['source'] == 'cloud-telemetry-agent'

    def test_alert_type_is_preserved(self):
        event = make_event(alert_type='ENDPOINT_DOWN')
        result = enrich_event(event)
        assert result['alert_type'] == 'ENDPOINT_DOWN'

    def test_message_is_preserved(self):
        event = make_event(message='original message text')
        result = enrich_event(event)
        assert result['message'] == 'original message text'


class TestEnrichAll:
    def test_enrich_all_processes_every_event(self):
        events = [make_event() for _ in range(4)]
        results = enrich_all(events)
        assert len(results) == 4

    def test_enrich_all_adds_labels_to_every_event(self):
        events = [make_event(), make_event(source='synthetic-uptime-monitor')]
        results = enrich_all(events)
        for result in results:
            assert 'source_label' in result
            assert 'alert_type_label' in result
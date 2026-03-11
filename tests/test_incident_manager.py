import pytest
from unittest.mock import patch, MagicMock
from pipeline.incident_manager import create_incident, log_incidents, close_incident, get_open_incidents


def make_routed_event(severity='HIGH', status='OPEN', source='cloud-telemetry-agent'):
    """Helper — build a fully routed event ready for incident creation."""
    return {
        'event_id': 'test-event-1234-abcd',
        'source': source,
        'source_label': 'Infrastructure Monitoring',
        'alert_type': 'THRESHOLD_BREACH',
        'alert_type_label': 'Metric Threshold Breach',
        'severity': severity,
        'urgency': 'PROMPT',
        'message': 'memory_percent is at 91% on test-server',
        'tags': ['memory'],
        'environment': 'production',
        'routed_channel': 'sns',
        'escalated': False
    }


class TestCreateIncident:
    def test_incident_contains_required_fields(self):
        event = make_routed_event()
        incident = create_incident(event)
        required_fields = [
            'incident_id', 'event_id', 'source', 'severity',
            'urgency', 'message', 'status', 'opened_at', 'closed_at', 'notes'
        ]
        for field in required_fields:
            assert field in incident, f"Missing field: {field}"

    def test_incident_status_is_open(self):
        event = make_routed_event()
        incident = create_incident(event)
        assert incident['status'] == 'OPEN'

    def test_incident_closed_at_is_none(self):
        event = make_routed_event()
        incident = create_incident(event)
        assert incident['closed_at'] is None

    def test_incident_notes_is_empty_list(self):
        event = make_routed_event()
        incident = create_incident(event)
        assert incident['notes'] == []

    def test_incident_id_starts_with_inc(self):
        event = make_routed_event()
        incident = create_incident(event)
        assert incident['incident_id'].startswith('INC-')

    def test_incident_severity_matches_event(self):
        event = make_routed_event(severity='CRITICAL')
        incident = create_incident(event)
        assert incident['severity'] == 'CRITICAL'

    def test_incident_source_matches_event(self):
        event = make_routed_event(source='synthetic-uptime-monitor')
        incident = create_incident(event)
        assert incident['source'] == 'synthetic-uptime-monitor'

    def test_incident_event_id_matches_event(self):
        event = make_routed_event()
        incident = create_incident(event)
        assert incident['event_id'] == 'test-event-1234-abcd'


class TestLogIncidents:
    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_log_incidents_returns_new_incidents(self, mock_load, mock_save):
        events = [make_routed_event(), make_routed_event(severity='CRITICAL')]
        new_incidents = log_incidents(events)
        assert len(new_incidents) == 2

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_log_incidents_calls_save(self, mock_load, mock_save):
        events = [make_routed_event()]
        log_incidents(events)
        mock_save.assert_called_once()

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_all_new_incidents_are_open(self, mock_load, mock_save):
        events = [make_routed_event(), make_routed_event()]
        new_incidents = log_incidents(events)
        for incident in new_incidents:
            assert incident['status'] == 'OPEN'

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_log_incidents_preserves_existing_incidents(self, mock_load, mock_save):
        existing = [{'incident_id': 'INC-EXISTING', 'status': 'OPEN'}]
        mock_load.return_value = existing
        events = [make_routed_event()]
        log_incidents(events)
        saved_incidents = mock_save.call_args[0][0]
        assert any(i['incident_id'] == 'INC-EXISTING' for i in saved_incidents)


class TestCloseIncident:
    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents')
    def test_close_incident_sets_status_to_closed(self, mock_load, mock_save):
        incident = create_incident(make_routed_event())
        mock_load.return_value = [incident]
        close_incident(incident['incident_id'])
        saved = mock_save.call_args[0][0]
        assert saved[0]['status'] == 'CLOSED'

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents')
    def test_close_incident_sets_closed_at_timestamp(self, mock_load, mock_save):
        incident = create_incident(make_routed_event())
        mock_load.return_value = [incident]
        close_incident(incident['incident_id'])
        saved = mock_save.call_args[0][0]
        assert saved[0]['closed_at'] is not None

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents')
    def test_close_incident_with_notes_appends_note(self, mock_load, mock_save):
        incident = create_incident(make_routed_event())
        mock_load.return_value = [incident]
        close_incident(incident['incident_id'], notes='Resolved by restarting service')
        saved = mock_save.call_args[0][0]
        assert len(saved[0]['notes']) == 1
        assert saved[0]['notes'][0]['note'] == 'Resolved by restarting service'

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_close_nonexistent_incident_returns_false(self, mock_load, mock_save):
        result = close_incident('INC-DOES-NOT-EXIST')
        assert result is False

    @patch('pipeline.incident_manager.save_incidents')
    @patch('pipeline.incident_manager.load_incidents')
    def test_close_incident_returns_true_on_success(self, mock_load, mock_save):
        incident = create_incident(make_routed_event())
        mock_load.return_value = [incident]
        result = close_incident(incident['incident_id'])
        assert result is True


class TestGetOpenIncidents:
    @patch('pipeline.incident_manager.load_incidents')
    def test_returns_only_open_incidents(self, mock_load):
        mock_load.return_value = [
            {'incident_id': 'INC-001', 'status': 'OPEN'},
            {'incident_id': 'INC-002', 'status': 'CLOSED'},
            {'incident_id': 'INC-003', 'status': 'OPEN'},
        ]
        result = get_open_incidents()
        assert len(result) == 2

    @patch('pipeline.incident_manager.load_incidents')
    def test_returns_empty_list_when_no_open_incidents(self, mock_load):
        mock_load.return_value = [
            {'incident_id': 'INC-001', 'status': 'CLOSED'},
        ]
        result = get_open_incidents()
        assert result == []

    @patch('pipeline.incident_manager.load_incidents', return_value=[])
    def test_returns_empty_list_when_no_incidents_exist(self, mock_load):
        result = get_open_incidents()
        assert result == []
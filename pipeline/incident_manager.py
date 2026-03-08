import json
import configparser
from datetime import datetime, timezone
from pathlib import Path

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

INCIDENT_DB = config['pipeline']['incident_db']


def load_incidents():
    path = Path(INCIDENT_DB)
    if not path.exists():
        return []
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('incidents', [])


def save_incidents(incidents):
    path = Path(INCIDENT_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump({'incidents': incidents}, f, indent=4)


def create_incident(event):
    """
    Creates a formal incident record from a routed alert event.
    """
    incident = {
        'incident_id': f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{event['event_id'][:8].upper()}",
        'event_id': event['event_id'],
        'source': event['source'],
        'source_label': event.get('source_label', event['source']),
        'alert_type': event['alert_type'],
        'alert_type_label': event.get('alert_type_label', event['alert_type']),
        'severity': event.get('severity', 'UNKNOWN'),
        'urgency': event.get('urgency', 'UNKNOWN'),
        'message': event['message'],
        'tags': event.get('tags', []),
        'environment': event.get('environment', 'unknown'),
        'routed_channel': event.get('routed_channel', 'unknown'),
        'escalated': event.get('escalated', False),
        'status': 'OPEN',
        'opened_at': datetime.now(timezone.utc).isoformat(),
        'closed_at': None,
        'notes': []
    }
    return incident


def log_incidents(routed_events):
    """
    Creates and persists incident records for all routed events.
    """
    incidents = load_incidents()
    new_incidents = []

    for event in routed_events:
        incident = create_incident(event)
        incidents.append(incident)
        new_incidents.append(incident)
        print(f"    📝 Incident created: {incident['incident_id']} [{incident['severity']}]")

    save_incidents(incidents)
    return new_incidents


def get_open_incidents():
    incidents = load_incidents()
    return [i for i in incidents if i['status'] == 'OPEN']


def close_incident(incident_id, notes=''):
    incidents = load_incidents()
    for incident in incidents:
        if incident['incident_id'] == incident_id:
            incident['status'] = 'CLOSED'
            incident['closed_at'] = datetime.now(timezone.utc).isoformat()
            if notes:
                incident['notes'].append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'note': notes
                })
            save_incidents(incidents)
            print(f"    ✅ Incident {incident_id} closed")
            return True
    print(f"    ❌ Incident {incident_id} not found")
    return False
import json
import configparser
import boto3

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

REGION = config['aws']['region']
SNS_TOPIC_ARN = config['aws']['sns_topic_arn']
RULES_FILE = config['routing']['rules_file']

client = boto3.client('sns', region_name=REGION)


def load_routing_rules():
    with open(RULES_FILE, 'r') as f:
        data = json.load(f)
    return data['routing_rules']


def match_rule(event, rules):
    """
    Matches an event to the highest priority routing rule.
    """
    matched_rule = None
    highest_priority = 999

    for rule in rules:
        conditions = rule['conditions']
        severity_match = (
            conditions['severity'] is None or
            conditions['severity'] == event.get('severity')
        )
        source_match = (
            conditions['source'] is None or
            conditions['source'] == event.get('source')
        )

        if severity_match and source_match:
            if rule['priority'] < highest_priority:
                highest_priority = rule['priority']
                matched_rule = rule

    return matched_rule


def route_event(event, rules):
    """
    Routes an event to the appropriate channel based on routing rules.
    """
    rule = match_rule(event, rules)

    if not rule:
        print(f"    ⚠️  No routing rule matched for {event['event_id']} — using default")
        channel = 'log'
        escalate = False
    else:
        channel = rule['channel']
        escalate = rule.get('escalate', False)
        print(f"    📋 Rule matched: '{rule['name']}' → channel: {channel.upper()}")

    routed = event.copy()
    routed['routed_channel'] = channel
    routed['escalated'] = escalate

    if channel == 'sns':
        send_sns_alert(event, escalate)

    return routed


def send_sns_alert(event, escalate):
    """
    Delivers alert via AWS SNS.
    """
    escalation_tag = '🚨 ESCALATED' if escalate else '⚠️'
    tags_str = ', '.join(event.get('tags', [])) or 'none'

    message = (
        f"{escalation_tag} INCIDENT ALERT\n\n"
        f"Source      : {event.get('source_label', event['source'])}\n"
        f"Type        : {event.get('alert_type_label', event['alert_type'])}\n"
        f"Severity    : {event.get('severity', 'UNKNOWN')}\n"
        f"Urgency     : {event.get('urgency', 'UNKNOWN')}\n"
        f"Environment : {event.get('environment', 'unknown')}\n"
        f"Tags        : {tags_str}\n\n"
        f"Message     : {event['message']}\n\n"
        f"Event ID    : {event['event_id']}\n"
        f"Received At : {event['received_at']}"
    )

    try:
        client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"[{event.get('severity', 'UNKNOWN')}] {event.get('alert_type_label', event['alert_type'])} — {event['source']}",
            Message=message
        )
        print(f"    ✅ SNS alert delivered")
    except Exception as e:
        print(f"    ❌ SNS delivery failed: {str(e)}")


def route_all(events):
    rules = load_routing_rules()
    routed = []
    for event in events:
        print(f"\n  Routing: [{event.get('severity')}] {event['message'][:60]}...")
        result = route_event(event, rules)
        routed.append(result)
    return routed
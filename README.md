# incident-alert-pipeline

A production-grade incident alert pipeline that ingests alert events from across a CloudOps ecosystem, enriches and classifies them by severity, routes them to the appropriate channel via configurable routing rules, and maintains a persistent incident database.

Built to mirror real-world NOC automation and incident management workflows.

---

## Overview

Real NOC environments don't just receive alerts — they process them. `incident-alert-pipeline` demonstrates a complete alert-to-incident workflow: raw events are ingested, enriched with operational context, classified by severity and urgency, routed to the right channel, and logged as formal incident records with unique IDs and timestamps.

This project demonstrates core NOC Automation and SRE competencies:
- Event ingestion and normalization
- Automated severity classification
- Rule-based alert routing
- AWS SNS multi-channel delivery
- Persistent incident lifecycle management

---

## Architecture
```
Alert Events (any source)
        │
        ▼
  ingestor.py         # Event normalization and standardization
        │
        ▼
  enricher.py         # Context enrichment — labels, tags, environment
        │
        ▼
  classifier.py       # Severity and urgency classification
        │
        ▼
  router.py           # Rule-based routing → AWS SNS or log
        │
        ▼
  incident_manager.py # Incident record creation and persistence
        │
        ▼
  data/incidents.json # Persistent incident database
```

---

## Features

- **Event normalization** — All alert sources produce a standardized event format
- **Contextual enrichment** — Human-readable labels, environment tags, operational context
- **Severity classification** — CRITICAL, HIGH, MEDIUM, LOW with urgency scoring
- **Rule-based routing** — JSON-configured routing rules with priority ordering
- **AWS SNS delivery** — Real alert delivery for CRITICAL and HIGH severity events
- **Incident database** — Persistent JSON incident log with open/closed lifecycle
- **Ecosystem integration** — Native support for events from all portfolio repos
- **Config-driven** — Zero hardcoded values

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.x |
| AWS SDK | boto3 / botocore |
| Alert Delivery | AWS SNS |
| Routing Rules | JSON |
| Incident Storage | JSON |
| Configuration | configparser |

---

## Project Structure
```
incident-alert-pipeline/
├── pipeline/
│   ├── __init__.py
│   ├── ingestor.py          # Event ingestion and normalization
│   ├── enricher.py          # Event enrichment
│   ├── classifier.py        # Severity classification
│   ├── router.py            # Rule-based routing
│   └── incident_manager.py  # Incident lifecycle management
├── config/
│   ├── config.ini           # Pipeline configuration
│   └── routing_rules.json   # Routing rule definitions
├── data/
│   └── incidents.json       # Persistent incident database
├── logs/
├── tests/
│   └── __init__.py
├── requirements.txt
└── main.py
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- AWS account (Free Tier compatible)
- AWS CLI installed and configured

### Installation
```bash
git clone https://github.com/Alex-CloudOps/incident-alert-pipeline.git
cd incident-alert-pipeline
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration

Edit `config/config.ini`:
```ini
[aws]
region = us-east-2
sns_topic_arn = arn:aws:sns:us-east-2:YOUR_ACCOUNT_ID:your-topic
```

### Routing Rules

Edit `config/routing_rules.json` to define your routing logic:
```json
{
    "routing_rules": [
        {
            "name": "Critical Infrastructure",
            "conditions": {
                "severity": "CRITICAL",
                "source": null
            },
            "channel": "sns",
            "escalate": true,
            "priority": 1
        }
    ]
}
```

### Run the Pipeline
```bash
python main.py
```

---

## Sample Output
```
============================================================
  INCIDENT ALERT PIPELINE
============================================================
📥 Ingesting alert events...
  → 5 event(s) received
🎯 Classifying severity...
  [CRITICAL] HTTPBin Simulated Failure is DOWN — status code 503
  [CRITICAL] cpu_percent is at 97.0% on prod-server-02
  [HIGH] memory_percent is at 91.0% on my-server-01
🚦 Routing events...
  📋 Rule matched: 'Critical Infrastructure' → channel: SNS
    ✅ SNS alert delivered
📝 Creating incident records...
    📝 Incident created: INC-20260308161020-E416C24A [CRITICAL]
============================================================
  ✅ PIPELINE COMPLETE
  Events Processed  : 5
  Incidents Created : 5
  Critical          : 3
  High              : 1
  Medium            : 1
============================================================
```

---

## Ecosystem Integration

This pipeline is designed to receive events from all repos in the Alex-CloudOps observability ecosystem:

| Source | Event Types |
|---|---|
| `cloud-telemetry-agent` | THRESHOLD_BREACH |
| `synthetic-uptime-monitor` | ENDPOINT_DOWN, SLOW_RESPONSE |
| `log-intelligence-engine` | HEALTH_DEGRADED, LOG_ANOMALY |

---

## Roadmap

- [ ] REST API endpoint for real-time event ingestion
- [ ] Slack and email routing channels
- [ ] Incident auto-close logic
- [ ] Escalation timer with follow-up alerts
- [ ] Power BI incident dashboard integration
- [x] Unit tests with pytest

---

## Author

**Alex Evans** | CloudOps & NOC Engineer
[GitHub](https://github.com/Alex-CloudOps) | alex.evans.cloudops@gmail.com

---

*Built to demonstrate production-grade NOC automation and incident management engineering practices.*
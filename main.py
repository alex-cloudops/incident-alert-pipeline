from pipeline.ingestor import load_sample_events
from pipeline.enricher import enrich_all
from pipeline.classifier import classify_all
from pipeline.router import route_all
from pipeline.incident_manager import log_incidents, get_open_incidents


if __name__ == "__main__":
    print("=" * 60)
    print("  INCIDENT ALERT PIPELINE")
    print("=" * 60)

    # Step 1: Ingest
    print("\n📥 Ingesting alert events...")
    events = load_sample_events()
    print(f"  → {len(events)} event(s) received")

    # Step 2: Enrich
    print("\n🔍 Enriching events...")
    enriched = enrich_all(events)
    print(f"  → {len(enriched)} event(s) enriched")

    # Step 3: Classify
    print("\n🎯 Classifying severity...")
    classified = classify_all(enriched)
    for e in classified:
        print(f"  [{e['severity']}] {e['message'][:60]}...")

    # Step 4: Route
    print("\n🚦 Routing events...")
    routed = route_all(classified)

    # Step 5: Log Incidents
    print("\n📝 Creating incident records...")
    new_incidents = log_incidents(routed)

    # Summary
    open_incidents = get_open_incidents()
    critical = sum(1 for i in new_incidents if i['severity'] == 'CRITICAL')
    high = sum(1 for i in new_incidents if i['severity'] == 'HIGH')
    medium = sum(1 for i in new_incidents if i['severity'] == 'MEDIUM')
    low = sum(1 for i in new_incidents if i['severity'] == 'LOW')

    print("\n" + "=" * 60)
    print(f"  ✅ PIPELINE COMPLETE")
    print(f"  Events Processed  : {len(events)}")
    print(f"  Incidents Created : {len(new_incidents)}")
    print(f"  Critical          : {critical}")
    print(f"  High              : {high}")
    print(f"  Medium            : {medium}")
    print(f"  Low               : {low}")
    print(f"  Total Open        : {len(open_incidents)}")
    print("=" * 60)
"""
Test script for AI Agents

Tests all three agents:
1. LinkedIn Research Agent
2. Follow-up Scheduler Agent
3. Network Analysis Agent

Run: python test_agents.py
"""

import json
import asyncio
from agents import (
    enrich_contact,
    ContactEnrichmentCrew,
    enrich_contact_with_linkedin,
    create_followup_strategy,
    analyze_network
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title.upper())
    print("="*70)


def test_linkedin_agent():
    """Test LinkedIn Research Agent"""
    print_section("Test 1: LinkedIn Research Agent")

    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment"],
        "conversation_summary": "Discussed AI safety work at Google"
    }

    print("\nInput Contact:")
    print(json.dumps(sample_contact, indent=2))

    print("\nRunning LinkedIn agent...")
    enriched = enrich_contact_with_linkedin(sample_contact)

    print("\nLinkedIn Profile:")
    if 'linkedin_profile' in enriched:
        profile = enriched['linkedin_profile']
        print(f"  Found: {profile['found']}")
        print(f"  Profile URL: {profile.get('profile_url', 'N/A')}")
        print(f"  Current Position: {profile.get('current_position', {}).get('title', 'N/A')}")
        print(f"  Connections: {profile.get('connections_count', 0)}")
        print(f"  Active: {profile.get('is_active', False)}")
        print(f"  Recent Topics: {', '.join(profile.get('recent_topics', []))}")

    print("\n[OK] LinkedIn agent test complete!")


def test_followup_agent():
    """Test Follow-up Scheduler Agent"""
    print_section("Test 2: Follow-up Scheduler Agent")

    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment", "Interpretability"],
        "follow_ups": ["Send GitHub repo", "Connect on LinkedIn"],
        "conversation_summary": "Discussed AI safety work at Google focusing on LLM alignment.",
        "met_at": "DevFest Kolkata 2026"
    }

    print("\nInput Contact:")
    print(json.dumps(sample_contact, indent=2))

    print("\nRunning Follow-up agent...")
    strategy = create_followup_strategy(sample_contact)

    print("\nFollow-up Strategy:")
    print(f"  Urgency: {strategy.get('urgency', 'N/A')}")
    print(f"  Priority Score: {strategy.get('priority_score', 0)}/100")
    print(f"  First Follow-up: {strategy.get('optimal_timing', {}).get('first_followup', 'N/A')}")
    print(f"  Recommended Medium: {strategy.get('optimal_timing', {}).get('medium', 'N/A')}")

    print("\n  Short Message:")
    print(f"  {strategy.get('messages', {}).get('short', 'N/A')}")

    print("\n  Action Items:")
    for item in strategy.get('action_items', [])[:3]:
        print(f"    - {item.get('item', 'N/A')} (by {item.get('deadline', 'N/A')})")

    print("\n  Value Adds:")
    for value_add in strategy.get('value_adds', [])[:3]:
        print(f"    - {value_add}")

    print("\n[OK] Follow-up agent test complete!")


def test_network_agent():
    """Test Network Analysis Agent"""
    print_section("Test 3: Network Analysis Agent")

    sample_contacts = [
        {
            "name": "Sarah Chen",
            "role": "ML Engineer",
            "company": "Google",
            "topics_discussed": ["AI safety", "Machine Learning"],
            "follow_ups": ["Send GitHub repo"],
            "met_at": "DevFest Kolkata 2026",
            "priority_score": 85
        },
        {
            "name": "John Smith",
            "role": "Product Manager",
            "company": "Microsoft",
            "topics_discussed": ["Product Development", "AI"],
            "follow_ups": ["Schedule call"],
            "met_at": "Tech Summit 2026",
            "priority_score": 75
        },
        {
            "name": "Emily Davis",
            "role": "Data Scientist",
            "company": "Google",
            "topics_discussed": ["Machine Learning", "Data Analysis"],
            "follow_ups": [],
            "met_at": "DevFest Kolkata 2026",
            "priority_score": 80
        }
    ]

    print(f"\nInput: {len(sample_contacts)} contacts")

    print("\nRunning Network agent...")
    analysis = analyze_network(sample_contacts)

    print("\nNetwork Metrics:")
    metrics = analysis.get('network_metrics', {})
    print(f"  Total Contacts: {metrics.get('total_contacts', 0)}")
    print(f"  Total Connections: {metrics.get('total_connections', 0)}")
    print(f"  Network Density: {metrics.get('network_density', 0):.2f}")

    print("\n  Key Connectors:")
    for connector in analysis.get('key_connectors', [])[:3]:
        print(f"    - {connector.get('name', 'N/A')} (impact: {connector.get('impact', 'N/A')})")

    print("\n  Introduction Suggestions:")
    for suggestion in analysis.get('introduction_suggestions', [])[:3]:
        print(f"    - Introduce {suggestion.get('introduce', 'N/A')} to {suggestion.get('to', 'N/A')}")
        print(f"      Reason: {suggestion.get('reason', 'N/A')}")

    print("\n  Network Insights:")
    for insight in analysis.get('insights', []):
        print(f"    - {insight}")

    print("\n[OK] Network agent test complete!")


def test_full_enrichment():
    """Test full contact enrichment with all agents"""
    print_section("Test 4: Full Contact Enrichment (All Agents)")

    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment", "Interpretability"],
        "follow_ups": ["Send GitHub repo", "Connect on LinkedIn"],
        "conversation_summary": "Discussed AI safety work at Google focusing on LLM alignment.",
        "met_at": "DevFest Kolkata 2026",
        "confidence_score": 0.87
    }

    print("\nInput Contact:")
    print(json.dumps(sample_contact, indent=2))

    print("\nRunning full enrichment...")
    enriched = enrich_contact(contact_data=sample_contact)

    print("\nEnrichment Results:")
    print(f"  Agents Run: {enriched.get('enrichment_metadata', {}).get('total_agents', 0)}")
    print(f"  Successful: {enriched.get('enrichment_metadata', {}).get('success_count', 0)}")

    if 'linkedin_profile' in enriched:
        print(f"\n  LinkedIn: FOUND")
        print(f"    - Profile: {enriched['linkedin_profile'].get('profile_url', 'N/A')}")
        print(f"    - Connections: {enriched['linkedin_profile'].get('connections_count', 0)}")

    if 'followup_strategy' in enriched:
        print(f"\n  Follow-up Strategy: CREATED")
        print(f"    - Priority: {enriched['followup_strategy'].get('priority_score', 0)}/100")
        print(f"    - Urgency: {enriched['followup_strategy'].get('urgency', 'N/A')}")
        print(f"    - First Action: {enriched['followup_strategy'].get('optimal_timing', {}).get('first_followup', 'N/A')}")

    print("\n[OK] Full enrichment test complete!")


def test_batch_enrichment():
    """Test batch enrichment with network analysis"""
    print_section("Test 5: Batch Enrichment with Network Analysis")

    sample_contacts = [
        {
            "name": "Sarah Chen",
            "role": "ML Engineer",
            "company": "Google",
            "topics_discussed": ["AI safety", "Machine Learning"],
            "met_at": "DevFest Kolkata 2026"
        },
        {
            "name": "John Smith",
            "role": "Product Manager",
            "company": "Microsoft",
            "topics_discussed": ["Product Development", "AI"],
            "met_at": "Tech Summit 2026"
        },
        {
            "name": "Emily Davis",
            "role": "Data Scientist",
            "company": "Google",
            "topics_discussed": ["Machine Learning", "Data Analysis"],
            "met_at": "DevFest Kolkata 2026"
        }
    ]

    print(f"\nEnriching {len(sample_contacts)} contacts...")

    crew = ContactEnrichmentCrew()
    result = crew.enrich_multiple_contacts(sample_contacts)

    print("\nBatch Results:")
    print(f"  Contacts Enriched: {result.get('batch_metadata', {}).get('successfully_enriched', 0)}")
    print(f"  Total Contacts: {result.get('batch_metadata', {}).get('total_contacts', 0)}")

    if result.get('network_analysis'):
        network = result['network_analysis']
        print(f"\n  Network Analysis:")
        print(f"    - Total Contacts: {network.get('network_metrics', {}).get('total_contacts', 0)}")
        print(f"    - Network Density: {network.get('network_metrics', {}).get('network_density', 0):.2f}")
        print(f"    - Key Connectors: {len(network.get('key_connectors', []))}")
        print(f"    - Introduction Suggestions: {len(network.get('introduction_suggestions', []))}")

    print("\n[OK] Batch enrichment test complete!")


def test_quick_insights():
    """Test quick insights function"""
    print_section("Test 6: Quick Insights")

    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI", "ML"],
        "follow_ups": ["Send repo"]
    }

    print("\nInput Contact:")
    print(json.dumps(sample_contact, indent=2))

    crew = ContactEnrichmentCrew()
    insights = crew.get_quick_insights(sample_contact)

    print("\nQuick Insights:")
    print(f"  Priority Level: {insights.get('priority_level', 'N/A')}")
    print(f"  Connection Value: {insights.get('connection_value', 'N/A')}")
    print(f"  Recommended Action: {insights.get('recommended_action', 'N/A')}")
    print(f"  Summary: {insights.get('quick_summary', 'N/A')}")

    print("\n[OK] Quick insights test complete!")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("NETWORKMEMORY AI AGENTS - COMPREHENSIVE TEST SUITE")
    print("="*70)

    try:
        # Test individual agents
        test_linkedin_agent()
        test_followup_agent()
        test_network_agent()

        # Test orchestration
        test_full_enrichment()
        test_batch_enrichment()
        test_quick_insights()

        # Summary
        print_section("Test Summary")
        print("\n  [OK] All 6 tests passed!")
        print("\n  Agents are ready for:")
        print("    1. API integration (main.py endpoints)")
        print("    2. Node.js backend calls")
        print("    3. React Native mobile app")
        print("\n  Next steps:")
        print("    1. Start the server: python main.py")
        print("    2. Test API endpoints: curl http://localhost:8000/api/agents/enrich")
        print("    3. Integrate with Node.js backend")

        return True

    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()

    if success:
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("[FAILED] Some tests failed. Check output above.")
        print("="*70 + "\n")

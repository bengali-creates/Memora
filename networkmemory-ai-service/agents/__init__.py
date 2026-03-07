"""
NetworkMemory AI Agents

This package contains 5 specialized AI agents for enriching contact information:
- LinkedIn Research Agent: Find and analyze LinkedIn profiles
- Follow-up Scheduler Agent: Create optimal follow-up strategies
- Network Analysis Agent: Analyze professional networks and find connectors
- Relationship Health Agent: Track and analyze relationship strength
- Introduction Broker Agent: Match contacts for strategic introductions

Usage:
    from agents import enrich_contact, ContactEnrichmentCrew

    # Enrich single contact (runs all applicable agents)
    enriched = enrich_contact(contact_data=my_contact)

    # Batch enrichment with network analysis and introductions
    crew = ContactEnrichmentCrew()
    result = crew.enrich_multiple_contacts([contact1, contact2, contact3])
"""

from .crew import (
    ContactEnrichmentCrew,
    enrich_contact,
    calculate_quick_priority,
    get_recommended_action,
    estimate_connection_value
)

from .linkedin_agent import enrich_contact_with_linkedin
from .followup_agent import create_followup_strategy
from .network_agent import analyze_network, NetworkGraph
from .relationship_agent import analyze_relationship_health, RelationshipHealthAnalyzer
from .introduction_agent import find_best_introductions, create_introduction_package

__all__ = [
    # Main crew orchestrator
    'ContactEnrichmentCrew',
    'enrich_contact',

    # Individual agents
    'enrich_contact_with_linkedin',
    'create_followup_strategy',
    'analyze_network',
    'NetworkGraph',
    'analyze_relationship_health',
    'RelationshipHealthAnalyzer',
    'find_best_introductions',
    'create_introduction_package',

    # Utility functions
    'calculate_quick_priority',
    'get_recommended_action',
    'estimate_connection_value',
]

__version__ = '2.0.0'  # Updated with 5 agents!

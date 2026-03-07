"""
Agent Crew Orchestrator

This module coordinates all 5 agents to enrich contact information.
Manages the complete workflow for contact enrichment and relationship management.

Workflow:
1. LinkedIn Agent: Enrich with professional data
2. Follow-up Agent: Create follow-up strategy
3. Network Agent: Analyze network position
4. Relationship Health Agent: Analyze relationship strength
5. Introduction Broker Agent: Find introduction opportunities
6. Return comprehensive enriched data
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from .linkedin_agent import enrich_contact_with_linkedin
from .followup_agent import create_followup_strategy
from .network_agent import analyze_network
from .relationship_agent import analyze_relationship_health, RelationshipHealthAnalyzer
from .introduction_agent import find_best_introductions, create_introduction_package


class ContactEnrichmentCrew:
    """
    Crew for enriching contact information using multiple agents

    This crew coordinates 5 specialized agents:
    - LinkedIn Research Agent: Professional data enrichment
    - Follow-up Scheduler Agent: Optimal follow-up strategies
    - Network Analysis Agent: Network position and introductions
    - Relationship Health Agent: Relationship strength tracking
    - Introduction Broker Agent: Strategic introduction matching
    """

    def __init__(self):
        """Initialize the crew"""
        self.agents_enabled = {
            'linkedin': True,
            'followup': True,
            'network': True,
            'relationship': True,
            'introductions': True
        }

    def enrich_single_contact(self, contact_data: Dict, include_network: bool = False) -> Dict:
        """
        Enrich a single contact using all available agents

        Args:
            contact_data: Contact information to enrich
            include_network: Whether to include network analysis (requires multiple contacts)

        Returns:
            Enriched contact data with:
            - linkedin_profile
            - followup_strategy
            - network_position (if include_network=True)
            - enrichment_metadata

        Example:
            >>> crew = ContactEnrichmentCrew()
            >>> enriched = crew.enrich_single_contact(contact_data)
            >>> print(enriched['followup_strategy']['messages']['short'])
        """
        print(f"\n[*] Starting contact enrichment: {contact_data.get('name', 'Unknown')}")

        enriched = contact_data.copy()
        enrichment_log = []

        # Step 1: LinkedIn Research
        if self.agents_enabled['linkedin']:
            try:
                print("[1/4] Running LinkedIn Research Agent...")
                linkedin_data = enrich_contact_with_linkedin(contact_data)
                enriched.update(linkedin_data)
                enrichment_log.append({
                    'agent': 'linkedin',
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
                print("[OK] LinkedIn enrichment complete")
            except Exception as e:
                print(f"[ERROR] LinkedIn enrichment failed: {e}")
                enrichment_log.append({
                    'agent': 'linkedin',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Step 2: Follow-up Strategy
        if self.agents_enabled['followup']:
            try:
                print("[2/4] Running Follow-up Scheduler Agent...")
                followup_data = create_followup_strategy(enriched)
                enriched['followup_strategy'] = followup_data
                enrichment_log.append({
                    'agent': 'followup',
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
                print("[OK] Follow-up strategy created")
            except Exception as e:
                print(f"[ERROR] Follow-up strategy failed: {e}")
                enrichment_log.append({
                    'agent': 'followup',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Step 3: Relationship Health
        if self.agents_enabled['relationship']:
            try:
                print("[3/4] Running Relationship Health Agent...")
                health_data = analyze_relationship_health(enriched)
                enriched['relationship_health'] = health_data
                enrichment_log.append({
                    'agent': 'relationship',
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
                print("[OK] Relationship health analyzed")
            except Exception as e:
                print(f"[ERROR] Relationship health analysis failed: {e}")
                enrichment_log.append({
                    'agent': 'relationship',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Step 4: Network Analysis (optional)
        if include_network and self.agents_enabled['network']:
            try:
                print("[4/4] Running Network Analysis Agent...")
                # Network analysis requires multiple contacts, so we'll mark it as pending
                enriched['network_analysis'] = {
                    'status': 'pending',
                    'message': 'Run batch enrichment to get network analysis'
                }
                enrichment_log.append({
                    'agent': 'network',
                    'status': 'skipped',
                    'reason': 'Requires multiple contacts',
                    'timestamp': datetime.utcnow().isoformat()
                })
                print("[INFO] Network analysis skipped (requires multiple contacts)")
            except Exception as e:
                print(f"[ERROR] Network analysis failed: {e}")
                enrichment_log.append({
                    'agent': 'network',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Add enrichment metadata
        enriched['enrichment_metadata'] = {
            'enriched_at': datetime.utcnow().isoformat(),
            'agents_run': enrichment_log,
            'success_count': sum(1 for log in enrichment_log if log['status'] == 'success'),
            'total_agents': len(enrichment_log)
        }

        print(f"[OK] Contact enrichment complete: {enriched['enrichment_metadata']['success_count']}/{enriched['enrichment_metadata']['total_agents']} agents succeeded")

        return enriched

    def enrich_multiple_contacts(self, contacts: List[Dict]) -> Dict:
        """
        Enrich multiple contacts and perform network analysis

        This is more powerful than single enrichment because:
        - Can analyze relationships between contacts
        - Can suggest introductions
        - Can identify key connectors

        Args:
            contacts: List of contact dictionaries

        Returns:
            Dictionary with:
            - enriched_contacts: List of enriched contacts
            - network_analysis: Network-wide insights
            - batch_metadata: Batch processing info

        Example:
            >>> crew = ContactEnrichmentCrew()
            >>> result = crew.enrich_multiple_contacts([contact1, contact2, contact3])
            >>> print(result['network_analysis']['key_connectors'])
        """
        print(f"\n[*] Starting batch enrichment for {len(contacts)} contacts")

        enriched_contacts = []

        # Step 1: Enrich each contact individually
        for i, contact in enumerate(contacts):
            print(f"\n[CONTACT {i+1}/{len(contacts)}] {contact.get('name', 'Unknown')}")
            enriched = self.enrich_single_contact(contact, include_network=False)
            enriched_contacts.append(enriched)

        # Step 2: Run network analysis on all contacts
        network_analysis = None
        if self.agents_enabled['network'] and len(enriched_contacts) > 1:
            try:
                print(f"\n[NETWORK ANALYSIS] Analyzing network of {len(enriched_contacts)} contacts...")
                network_analysis = analyze_network(enriched_contacts)
                print("[OK] Network analysis complete")
            except Exception as e:
                print(f"[ERROR] Network analysis failed: {e}")
                network_analysis = {'error': str(e)}

        # Step 3: Find introduction opportunities
        introduction_opportunities = None
        if self.agents_enabled['introductions'] and len(enriched_contacts) > 1:
            try:
                print(f"\n[INTRODUCTION BROKER] Finding introduction opportunities...")
                introduction_opportunities = find_best_introductions(enriched_contacts, top_n=10)
                print(f"[OK] Found {len(introduction_opportunities)} introduction opportunities")
            except Exception as e:
                print(f"[ERROR] Introduction matching failed: {e}")
                introduction_opportunities = []

        # Build result
        result = {
            'enriched_contacts': enriched_contacts,
            'network_analysis': network_analysis,
            'introduction_opportunities': introduction_opportunities,
            'batch_metadata': {
                'total_contacts': len(contacts),
                'successfully_enriched': len(enriched_contacts),
                'introduction_opportunities_found': len(introduction_opportunities) if introduction_opportunities else 0,
                'processed_at': datetime.utcnow().isoformat()
            }
        }

        print(f"\n[OK] Batch enrichment complete: {len(enriched_contacts)} contacts processed")
        if introduction_opportunities:
            print(f"[OK] {len(introduction_opportunities)} introduction opportunities identified")

        return result

    def get_quick_insights(self, contact_data: Dict) -> Dict:
        """
        Get quick insights about a contact without full enrichment

        Useful for:
        - Quick preview before full enrichment
        - Mobile app quick view
        - Real-time suggestions

        Args:
            contact_data: Contact information

        Returns:
            Quick insights dictionary
        """
        name = contact_data.get('name', 'Unknown')
        role = contact_data.get('role', '')
        company = contact_data.get('company', '')
        topics = contact_data.get('topics_discussed', [])

        insights = {
            'priority_level': calculate_quick_priority(contact_data),
            'recommended_action': get_recommended_action(contact_data),
            'key_topics': topics[:3] if topics else [],
            'connection_value': estimate_connection_value(role, company),
            'quick_summary': generate_quick_summary(name, role, company, topics)
        }

        return insights


def calculate_quick_priority(contact_data: Dict) -> str:
    """Calculate quick priority level (high/medium/low)"""
    role = contact_data.get('role', '').lower()
    action_items = contact_data.get('follow_ups', [])

    if any(title in role for title in ['ceo', 'founder', 'director', 'vp']):
        return 'high'
    elif len(action_items) > 0:
        return 'high'
    elif any(title in role for title in ['lead', 'senior', 'manager']):
        return 'medium'
    else:
        return 'medium'


def get_recommended_action(contact_data: Dict) -> str:
    """Get recommended next action"""
    action_items = contact_data.get('follow_ups', [])

    if action_items:
        return f"Complete: {action_items[0]}"
    else:
        return "Send follow-up message within 24 hours"


def estimate_connection_value(role: str, company: str) -> str:
    """Estimate connection value (high/medium/low)"""
    role_lower = role.lower() if role else ''
    company_lower = company.lower() if company else ''

    # High value indicators
    if any(title in role_lower for title in ['ceo', 'founder', 'director', 'vp', 'head']):
        return 'high'

    if any(name in company_lower for name in ['google', 'microsoft', 'amazon', 'meta', 'apple']):
        return 'high'

    # Medium value by default
    return 'medium'


def generate_quick_summary(name: str, role: str, company: str, topics: List[str]) -> str:
    """Generate one-sentence summary"""
    if company and role:
        summary = f"{name} is a {role} at {company}"
    elif company:
        summary = f"{name} works at {company}"
    elif role:
        summary = f"{name} is a {role}"
    else:
        summary = f"Met {name}"

    if topics:
        summary += f", interested in {topics[0]}"

    return summary


# Convenience function for API endpoint
def enrich_contact(contact_id: str = None, contact_data: Dict = None) -> Dict:
    """
    Convenience function to enrich a contact

    Can be called with either contact_id (will fetch from DB)
    or contact_data (direct enrichment)

    Args:
        contact_id: Database ID of contact to enrich
        contact_data: Contact data dictionary

    Returns:
        Enriched contact data

    Example:
        >>> enriched = enrich_contact(contact_data=my_contact)
        >>> print(enriched['followup_strategy'])
    """
    if not contact_data and not contact_id:
        raise ValueError("Must provide either contact_id or contact_data")

    if contact_id:
        # TODO: Fetch from database
        # For now, raise error
        raise NotImplementedError("Database fetching not yet implemented")

    crew = ContactEnrichmentCrew()
    return crew.enrich_single_contact(contact_data)


# Example usage
if __name__ == "__main__":
    # Test with sample contact
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

    print("\n" + "="*70)
    print("TESTING CONTACT ENRICHMENT CREW")
    print("="*70)

    crew = ContactEnrichmentCrew()

    # Test single contact enrichment
    enriched = crew.enrich_single_contact(sample_contact)

    print("\n" + "-"*70)
    print("ENRICHED CONTACT:")
    print("-"*70)
    print(json.dumps(enriched, indent=2))

    # Test quick insights
    print("\n" + "-"*70)
    print("QUICK INSIGHTS:")
    print("-"*70)
    insights = crew.get_quick_insights(sample_contact)
    print(json.dumps(insights, indent=2))

    print("\n" + "="*70)
    print("[OK] Agent crew test complete!")
    print("="*70)

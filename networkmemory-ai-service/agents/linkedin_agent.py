"""
LinkedIn Research Agent

This agent enriches contact information by researching LinkedIn profiles.
Uses CrewAI for agent orchestration and task management.

Capabilities:
1. Search LinkedIn for contact name + company
2. Extract profile information
3. Find mutual connections
4. Analyze profile activity
5. Suggest connection strategies
"""

from crewai import Agent, Task
from typing import Dict, Optional
from config import settings


def create_linkedin_researcher() -> Agent:
    """
    Create LinkedIn research agent

    This agent specializes in finding and analyzing LinkedIn profiles
    to enrich contact information.

    Returns:
        Agent configured for LinkedIn research
    """
    return Agent(
        role='LinkedIn Research Specialist',
        goal='Find and analyze LinkedIn profiles to enrich contact information with professional details',
        backstory="""You are an expert at finding people on LinkedIn and extracting
        valuable professional information. You understand how to search effectively,
        analyze profiles, and identify key details that help build meaningful
        professional relationships. You're skilled at finding mutual connections
        and understanding career trajectories.""",
        verbose=True,
        allow_delegation=False,
        # Tools will be added when we implement LinkedIn scraping
        tools=[]
    )


def create_linkedin_research_task(agent: Agent, contact_data: Dict) -> Task:
    """
    Create a task for the LinkedIn agent to research a contact

    Args:
        agent: The LinkedIn researcher agent
        contact_data: Dictionary with contact information (name, company, role, etc.)

    Returns:
        Task configured for LinkedIn research
    """
    name = contact_data.get('name', 'Unknown')
    company = contact_data.get('company', '')
    role = contact_data.get('role', '')

    # Build search query
    search_query = f"{name}"
    if company:
        search_query += f" at {company}"
    if role:
        search_query += f" - {role}"

    description = f"""
    Research LinkedIn profile for: {search_query}

    Your task:
    1. Search LinkedIn for this person using their name, company, and role
    2. If found, extract the following information:
       - LinkedIn profile URL
       - Current position and company
       - Previous work experience (last 2-3 positions)
       - Education background
       - Top skills
       - Number of connections (if visible)
       - Recent activity or posts (if public)
       - Mutual connections (if any)

    3. Analyze their profile to answer:
       - Are they active on LinkedIn?
       - What topics do they post about?
       - What's their career trajectory?
       - Are they currently hiring or looking for opportunities?

    4. Suggest connection strategy:
       - Best approach to connect (cold request vs mutual intro)
       - Personalized message template based on their interests
       - Common ground topics from their profile

    Original contact data:
    {format_contact_data(contact_data)}

    NOTE: If LinkedIn is not accessible, provide mock enriched data based on
    the role and company information to demonstrate the capability.
    """

    expected_output = """
    A structured JSON response with:
    {
        "found": true/false,
        "profile_url": "linkedin.com/in/...",
        "current_position": {
            "title": "...",
            "company": "...",
            "duration": "..."
        },
        "previous_experience": [
            {"title": "...", "company": "...", "duration": "..."}
        ],
        "education": [
            {"degree": "...", "school": "...", "year": "..."}
        ],
        "skills": ["skill1", "skill2", ...],
        "connections_count": 500,
        "is_active": true/false,
        "recent_topics": ["AI", "Machine Learning", ...],
        "career_insights": "Brief analysis of career trajectory",
        "connection_strategy": {
            "approach": "mutual_intro" or "cold_request",
            "message_template": "Personalized connection request",
            "common_ground": ["topic1", "topic2", ...]
        },
        "mutual_connections": ["Name 1", "Name 2", ...],
        "confidence_score": 0.85
    }
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )


def format_contact_data(contact_data: Dict) -> str:
    """Format contact data for display in task description"""
    formatted = []
    for key, value in contact_data.items():
        if value and key not in ['raw_conversation', 'extraction_time']:
            formatted.append(f"  - {key}: {value}")
    return "\n".join(formatted)


def enrich_contact_with_linkedin(contact_data: Dict) -> Dict:
    """
    Main function to enrich a contact using LinkedIn research

    Args:
        contact_data: Dictionary with contact information

    Returns:
        Enriched contact data with LinkedIn information

    Example:
        >>> contact = {"name": "Sarah Chen", "company": "Google", "role": "ML Engineer"}
        >>> enriched = enrich_contact_with_linkedin(contact)
        >>> print(enriched['linkedin_profile'])
    """
    try:
        # Create agent
        linkedin_agent = create_linkedin_researcher()

        # Create task
        research_task = create_linkedin_research_task(linkedin_agent, contact_data)

        # For now, return mock data until we implement actual LinkedIn scraping
        # In production, you would:
        # 1. Use linkedin-api package (requires authentication)
        # 2. Or use web scraping with Selenium/Playwright
        # 3. Or integrate with LinkedIn API (requires partnership)

        mock_enrichment = create_mock_linkedin_data(contact_data)

        # Merge with original data
        enriched_data = {**contact_data, **mock_enrichment}

        return enriched_data

    except Exception as e:
        print(f"[ERROR] LinkedIn enrichment failed: {e}")
        # Return original data if enrichment fails
        return contact_data


def create_mock_linkedin_data(contact_data: Dict) -> Dict:
    """
    Create mock LinkedIn data for demonstration

    In production, this would be replaced with actual LinkedIn API calls
    or web scraping. For hackathon demo, we'll generate realistic mock data.

    Args:
        contact_data: Original contact information

    Returns:
        Mock LinkedIn enrichment data
    """
    name = contact_data.get('name', 'Unknown')
    company = contact_data.get('company', 'Unknown Company')
    role = contact_data.get('role', 'Professional')

    # Generate realistic mock data based on role and company
    mock_data = {
        'linkedin_profile': {
            'found': True,
            'profile_url': f'https://linkedin.com/in/{name.lower().replace(" ", "-")}',
            'current_position': {
                'title': role,
                'company': company,
                'duration': '2 years 3 months'
            },
            'previous_experience': [
                {
                    'title': f'Senior {role.replace("Lead", "").replace("Senior", "").strip()}',
                    'company': 'Previous Company Inc.',
                    'duration': '3 years'
                },
                {
                    'title': role.replace('Lead', '').replace('Senior', '').strip(),
                    'company': 'Startup Co.',
                    'duration': '2 years'
                }
            ],
            'education': [
                {
                    'degree': 'Master of Science',
                    'school': 'Top University',
                    'year': '2015'
                },
                {
                    'degree': 'Bachelor of Science',
                    'school': 'State University',
                    'year': '2013'
                }
            ],
            'skills': [
                'Machine Learning',
                'Python',
                'TensorFlow',
                'Leadership',
                'Product Development'
            ],
            'connections_count': 892,
            'is_active': True,
            'recent_topics': ['AI', 'Machine Learning', 'Tech Innovation', 'Team Building'],
            'career_insights': f'{name} has shown consistent growth in the {role.lower()} space, '
                             f'moving from individual contributor to leadership roles. '
                             f'Active in the tech community and passionate about innovation.',
            'connection_strategy': {
                'approach': 'personalized_request',
                'message_template': f'Hi {name.split()[0]}, I enjoyed our conversation about '
                                  f'{contact_data.get("topics_discussed", ["innovation"])[0] if contact_data.get("topics_discussed") else "innovation"}. '
                                  f'Would love to stay connected and continue the discussion!',
                'common_ground': contact_data.get('topics_discussed', ['Technology', 'Innovation'])[:3]
            },
            'mutual_connections': ['Mutual Contact 1', 'Mutual Contact 2'],
            'confidence_score': 0.85,
            'enrichment_timestamp': '2026-03-05T12:00:00Z'
        }
    }

    return mock_data


# Example usage
if __name__ == "__main__":
    # Test the agent with sample contact data
    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment", "Interpretability"],
        "conversation_summary": "Discussed AI safety work at Google"
    }

    print("\n" + "="*70)
    print("TESTING LINKEDIN RESEARCH AGENT")
    print("="*70)

    enriched = enrich_contact_with_linkedin(sample_contact)

    print("\nEnriched Contact Data:")
    import json
    print(json.dumps(enriched, indent=2))

    print("\n" + "="*70)
    print("[OK] LinkedIn agent test complete!")
    print("="*70)

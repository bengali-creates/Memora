"""
Introduction Broker Agent

This agent matches contacts for strategic introductions that create mutual value.
Uses intelligent matchmaking to facilitate valuable connections.

Capabilities:
1. Match contacts based on interests, goals, and needs
2. Calculate introduction value for both parties
3. Generate compelling introduction messages
4. Identify timing and context for introductions
5. Track introduction outcomes
6. Suggest follow-up after introductions
"""

from crewai import Agent, Task
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


def create_introduction_broker() -> Agent:
    """
    Create introduction broker agent

    This agent specializes in matchmaking contacts for mutual benefit.

    Returns:
        Agent configured for introduction brokering
    """
    return Agent(
        role='Professional Introduction Broker',
        goal='Match contacts for strategic introductions that create mutual value and strengthen the network',
        backstory="""You are an expert at professional matchmaking and understanding
        what makes a valuable introduction. You know how to identify complementary skills,
        shared interests, and potential synergies. You craft compelling introduction
        messages that clearly communicate the value for both parties. You understand
        the art of warm introductions and how to make them successful.""",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )


class IntroductionMatcher:
    """
    Intelligent introduction matching system

    Finds high-value introduction opportunities in a network
    """

    @staticmethod
    def find_introduction_opportunities(contacts: List[Dict]) -> List[Dict]:
        """
        Find all potential introduction opportunities in a network

        Args:
            contacts: List of contacts to analyze

        Returns:
            List of introduction opportunities ranked by value
        """
        opportunities = []

        # Compare every pair of contacts
        for i, contact1 in enumerate(contacts):
            for contact2 in contacts[i+1:]:
                # Skip if they already know each other (would need connection data)
                # For now, assume they don't know each other

                opportunity = analyze_introduction_opportunity(contact1, contact2)

                if opportunity['value_score'] > 30:  # Threshold for worthwhile intro
                    opportunities.append(opportunity)

        # Sort by value score
        opportunities.sort(key=lambda x: x['value_score'], reverse=True)

        return opportunities

    @staticmethod
    def create_introduction(contact1: Dict, contact2: Dict, introduction_reason: str = None) -> Dict:
        """
        Create a complete introduction package

        Args:
            contact1: First contact to introduce
            contact2: Second contact to introduce
            introduction_reason: Optional custom reason

        Returns:
            Complete introduction package with messages
        """
        # Analyze the opportunity
        opportunity = analyze_introduction_opportunity(contact1, contact2)

        # Generate introduction messages
        messages = generate_introduction_messages(contact1, contact2, opportunity)

        # Suggest timing and follow-up
        timing = suggest_introduction_timing(contact1, contact2)
        followup = suggest_introduction_followup(contact1, contact2)

        return {
            'opportunity': opportunity,
            'messages': messages,
            'timing': timing,
            'followup_strategy': followup,
            'created_at': datetime.utcnow().isoformat()
        }


def analyze_introduction_opportunity(contact1: Dict, contact2: Dict) -> Dict:
    """
    Analyze potential value of introducing two contacts

    Considers:
    - Shared interests/topics
    - Complementary roles/skills
    - Industry overlap
    - Potential collaboration opportunities
    - Mutual benefit

    Args:
        contact1: First contact
        contact2: Second contact

    Returns:
        Opportunity analysis with value score
    """
    name1 = contact1.get('name', 'Person 1')
    name2 = contact2.get('name', 'Person 2')

    # Find shared interests
    topics1 = set(contact1.get('topics_discussed', []))
    topics2 = set(contact2.get('topics_discussed', []))
    shared_topics = topics1 & topics2

    # Check industry/company overlap
    company1 = contact1.get('company', '').lower()
    company2 = contact2.get('company', '').lower()
    same_company = company1 == company2 and company1 != ''

    # Check role complementarity
    role1 = contact1.get('role', '').lower()
    role2 = contact2.get('role', '').lower()
    complementary_roles = check_role_complementarity(role1, role2)

    # Calculate value score
    value_score = calculate_introduction_value(
        shared_topics, same_company, complementary_roles,
        contact1, contact2
    )

    # Generate introduction reason
    reason = generate_introduction_reason(
        name1, name2, shared_topics, same_company,
        complementary_roles, role1, role2, company1, company2
    )

    # Identify mutual benefits
    benefits = identify_mutual_benefits(
        contact1, contact2, shared_topics,
        complementary_roles, same_company
    )

    return {
        'contact1': {
            'name': name1,
            'role': contact1.get('role'),
            'company': contact1.get('company')
        },
        'contact2': {
            'name': name2,
            'role': contact2.get('role'),
            'company': contact2.get('company')
        },
        'shared_interests': list(shared_topics),
        'same_company': same_company,
        'complementary_roles': complementary_roles,
        'value_score': value_score,
        'introduction_reason': reason,
        'mutual_benefits': benefits,
        'confidence': calculate_confidence(value_score, shared_topics, complementary_roles)
    }


def check_role_complementarity(role1: str, role2: str) -> bool:
    """Check if two roles complement each other"""
    complementary_pairs = [
        (['engineer', 'developer', 'technical'], ['product', 'manager', 'pm']),
        (['designer', 'ux', 'ui'], ['product', 'manager', 'engineer']),
        (['sales', 'business'], ['engineer', 'technical', 'developer']),
        (['marketing', 'growth'], ['product', 'engineer']),
        (['founder', 'ceo'], ['investor', 'vc', 'advisor']),
        (['data', 'scientist', 'analyst'], ['engineer', 'manager', 'product'])
    ]

    for pair1, pair2 in complementary_pairs:
        has_role1 = any(keyword in role1 for keyword in pair1)
        has_role2 = any(keyword in role2 for keyword in pair2)

        if (has_role1 and has_role2) or (has_role2 and has_role1):
            return True

    return False


def calculate_introduction_value(shared_topics: set, same_company: bool,
                                 complementary_roles: bool,
                                 contact1: Dict, contact2: Dict) -> float:
    """Calculate introduction value score (0-100)"""
    score = 0

    # Shared interests are valuable
    score += len(shared_topics) * 20  # Up to 60 for 3+ shared topics

    # Same company but different roles = high value
    if same_company and not complementary_roles:
        score += 25
    elif same_company and complementary_roles:
        score += 40  # Very high value

    # Complementary roles even in different companies
    if complementary_roles:
        score += 20

    # Priority contacts get boost
    priority1 = contact1.get('priority_score', 50)
    priority2 = contact2.get('priority_score', 50)
    if priority1 >= 80 and priority2 >= 80:
        score += 15

    # Cap at 100
    return min(score, 100)


def generate_introduction_reason(name1: str, name2: str, shared_topics: set,
                                 same_company: bool, complementary_roles: bool,
                                 role1: str, role2: str, company1: str, company2: str) -> str:
    """Generate compelling introduction reason"""
    reasons = []

    if shared_topics:
        topics_str = ', '.join(list(shared_topics)[:2])
        reasons.append(f"both passionate about {topics_str}")

    if same_company:
        reasons.append(f"both at {company1.title()}")

    if complementary_roles:
        reasons.append(f"complementary expertise ({role1} and {role2})")

    if not reasons:
        reasons.append("potential synergy in professional interests")

    reason_str = " and ".join(reasons[:2])  # Max 2 reasons for brevity
    return f"I think {name1} and {name2} should connect - {reason_str}."


def identify_mutual_benefits(contact1: Dict, contact2: Dict, shared_topics: set,
                             complementary_roles: bool, same_company: bool) -> Dict:
    """Identify specific benefits for each party"""
    name1 = contact1.get('name', 'Person 1')
    name2 = contact2.get('name', 'Person 2')
    role1 = contact1.get('role', 'professional')
    role2 = contact2.get('role', 'professional')

    benefits = {
        'for_contact1': [],
        'for_contact2': [],
        'mutual': []
    }

    # Role-based benefits
    if 'engineer' in role1.lower() and 'product' in role2.lower():
        benefits['for_contact1'].append(f"Product perspective from {name2}")
        benefits['for_contact2'].append(f"Technical insights from {name1}")

    if 'manager' in role1.lower() or 'lead' in role1.lower():
        benefits['for_contact2'].append(f"Leadership mentorship from {name1}")

    if 'manager' in role2.lower() or 'lead' in role2.lower():
        benefits['for_contact1'].append(f"Leadership mentorship from {name2}")

    # Shared topics benefits
    if shared_topics:
        topic = list(shared_topics)[0]
        benefits['mutual'].append(f"Collaborate on {topic} projects")
        benefits['mutual'].append(f"Share knowledge about {topic}")

    # Same company benefits
    if same_company:
        benefits['mutual'].append("Build stronger internal network")
        benefits['mutual'].append("Potential cross-team collaboration")

    # Generic benefits if none found
    if not any(benefits.values()):
        benefits['mutual'] = [
            "Expand professional network",
            "Share industry insights",
            "Potential future collaboration"
        ]

    return benefits


def calculate_confidence(value_score: float, shared_topics: set, complementary_roles: bool) -> str:
    """Calculate confidence level in introduction success"""
    if value_score >= 70 and (shared_topics or complementary_roles):
        return 'very_high'
    elif value_score >= 50:
        return 'high'
    elif value_score >= 30:
        return 'medium'
    else:
        return 'low'


def generate_introduction_messages(contact1: Dict, contact2: Dict, opportunity: Dict) -> Dict:
    """
    Generate introduction messages

    Creates:
    1. Email introduction (formal, to both parties)
    2. LinkedIn message introduction (casual)
    3. Double opt-in request messages (to each party)
    """
    name1 = contact1.get('name', 'Person 1')
    name2 = contact2.get('name', 'Person 2')
    first_name1 = name1.split()[0]
    first_name2 = name2.split()[0]

    role1 = contact1.get('role', 'professional')
    role2 = contact2.get('role', 'professional')
    company1 = contact1.get('company', 'their company')
    company2 = contact2.get('company', 'their company')

    reason = opportunity.get('introduction_reason', '')
    shared_interests = opportunity.get('shared_interests', [])
    benefits = opportunity.get('mutual_benefits', {})

    # Email introduction (both parties)
    email_intro = f"""Subject: Introduction: {first_name1} <> {first_name2}

Hi {first_name1} and {first_name2},

I wanted to introduce you two - {reason}

{first_name1} is a {role1} at {company1}, and {first_name2} is a {role2} at {company2}.

{generate_connection_details(shared_interests, benefits)}

I think there's great potential for collaboration and mutual learning. I'll let you two take it from here!

Best,
[Your Name]

---
{first_name1}: {contact1.get('email', 'email')}
{first_name2}: {contact2.get('email', 'email')}"""

    # LinkedIn message (casual) - avoid backslash in f-string
    shared_topic = shared_interests[0] if shared_interests else "your shared interests"

    linkedin_intro = f"""Hi {first_name1} and {first_name2}!

Wanted to connect you two - {reason}

{first_name1}: {role1} at {company1}
{first_name2}: {role2} at {company2}

{shared_topic}! Let's grab coffee sometime?"""

    # Double opt-in requests - avoid backslash in f-string
    reason_for_1 = reason.replace(name1, 'You').replace(name2, first_name2)
    benefit_for_1 = benefits.get('for_contact1', [])[0] if benefits.get('for_contact1') else 'Could be valuable for your work.'

    opt_in_to_contact1 = f"""Hi {first_name1},

I know someone who I think you'd really benefit from meeting - {name2}, a {role2} at {company2}.

{reason_for_1}

{benefit_for_1}

Would you be open to an introduction?"""

    reason_for_2 = reason.replace(name2, 'You').replace(name1, first_name1)
    benefit_for_2 = benefits.get('for_contact2', [])[0] if benefits.get('for_contact2') else 'Could be valuable for your work.'

    opt_in_to_contact2 = f"""Hi {first_name2},

I know someone who I think you'd really benefit from meeting - {name1}, a {role1} at {company1}.

{reason_for_2}

{benefit_for_2}

Would you be open to an introduction?"""

    return {
        'email_introduction': email_intro,
        'linkedin_message': linkedin_intro,
        'opt_in_request_contact1': opt_in_to_contact1,
        'opt_in_request_contact2': opt_in_to_contact2
    }


def generate_connection_details(shared_interests: List[str], benefits: Dict) -> str:
    """Generate connection details paragraph"""
    parts = []

    if shared_interests:
        parts.append(f"You both have experience with {', '.join(shared_interests[:2])}.")

    mutual_benefits = benefits.get('mutual', [])
    if mutual_benefits:
        parts.append(f"Some potential areas of collaboration: {mutual_benefits[0].lower()}.")

    return " ".join(parts) if parts else "I think you'd have a great conversation!"


def suggest_introduction_timing(contact1: Dict, contact2: Dict) -> Dict:
    """Suggest optimal timing for introduction"""
    # For demo, suggest immediate introduction
    # In production, consider factors like:
    # - Relationship health with both parties
    # - Recent interactions
    # - Busy seasons

    return {
        'recommended_timing': 'immediate',
        'reason': 'Both relationships are active and healthy',
        'best_day': datetime.now().strftime('%A'),
        'best_time': '10:00 AM'  # Mid-morning
    }


def suggest_introduction_followup(contact1: Dict, contact2: Dict) -> Dict:
    """Suggest follow-up strategy after introduction"""
    name1 = contact1.get('name', 'Person 1')
    name2 = contact2.get('name', 'Person 2')

    return {
        'check_in_timing': '1 week after introduction',
        'check_in_message': f"Hi! Just wanted to check if you and {name2.split()[0]} had a chance to connect?",
        'success_indicators': [
            'They schedule a meeting',
            'They connect on LinkedIn',
            'They mention collaboration opportunities'
        ],
        'if_no_response': f"Send gentle nudge to both parties after 2 weeks"
    }


# Convenience functions
def find_best_introductions(contacts: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Find the best introduction opportunities in a network

    Args:
        contacts: List of contacts
        top_n: Number of top opportunities to return

    Returns:
        List of top introduction opportunities

    Example:
        >>> opportunities = find_best_introductions(my_contacts, top_n=3)
        >>> print(opportunities[0]['introduction_reason'])
    """
    matcher = IntroductionMatcher()
    opportunities = matcher.find_introduction_opportunities(contacts)
    return opportunities[:top_n]


def create_introduction_package(contact1: Dict, contact2: Dict) -> Dict:
    """
    Create complete introduction package

    Args:
        contact1: First contact
        contact2: Second contact

    Returns:
        Complete introduction package

    Example:
        >>> package = create_introduction_package(sarah, john)
        >>> print(package['messages']['email_introduction'])
    """
    matcher = IntroductionMatcher()
    return matcher.create_introduction(contact1, contact2)


# Example usage
if __name__ == "__main__":
    # Test with sample contacts
    contact1 = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "Machine Learning"],
        "priority_score": 85
    }

    contact2 = {
        "name": "John Smith",
        "role": "Product Manager",
        "company": "Microsoft",
        "topics_discussed": ["AI", "Product Development"],
        "priority_score": 75
    }

    contact3 = {
        "name": "Emily Davis",
        "role": "Data Scientist",
        "company": "Google",
        "topics_discussed": ["Machine Learning", "Data Analysis"],
        "priority_score": 80
    }

    print("\n" + "="*70)
    print("TESTING INTRODUCTION BROKER AGENT")
    print("="*70)

    # Test finding opportunities
    print("\nFinding introduction opportunities...")
    opportunities = find_best_introductions([contact1, contact2, contact3])

    print(f"\nFound {len(opportunities)} opportunities:")
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['contact1']['name']} <> {opp['contact2']['name']}")
        print(f"   Value Score: {opp['value_score']}/100")
        print(f"   Reason: {opp['introduction_reason']}")

    # Test creating introduction package
    if opportunities:
        print("\n" + "-"*70)
        print("Creating introduction package for top opportunity...")
        package = create_introduction_package(contact1, contact3)

        print("\nEmail Introduction:")
        print(package['messages']['email_introduction'][:200] + "...")

    print("\n" + "="*70)
    print("[OK] Introduction broker agent test complete!")
    print("="*70)

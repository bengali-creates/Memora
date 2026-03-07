"""
Follow-up Scheduler Agent

This agent analyzes conversations and suggests optimal follow-up timing and strategies.
Uses AI to prioritize contacts and generate personalized follow-up messages.

Capabilities:
1. Analyze conversation urgency and importance
2. Suggest optimal follow-up timing
3. Generate personalized follow-up messages
4. Prioritize contacts by potential value
5. Identify action items from conversation
"""

from crewai import Agent, Task
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


def create_followup_scheduler() -> Agent:
    """
    Create follow-up scheduler agent

    This agent specializes in analyzing conversations to determine
    the best follow-up strategy and timing.

    Returns:
        Agent configured for follow-up scheduling
    """
    return Agent(
        role='Follow-up Strategy Specialist',
        goal='Analyze conversations and create optimal follow-up strategies to build strong professional relationships',
        backstory="""You are an expert at relationship management and communication timing.
        You understand the psychology of follow-ups, knowing when to reach out, what to say,
        and how to prioritize contacts. You're skilled at identifying action items, detecting
        urgency, and crafting personalized messages that resonate. You help people build
        meaningful professional relationships by ensuring they follow up at the right time
        with the right message.""",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )


def create_followup_task(agent: Agent, contact_data: Dict) -> Task:
    """
    Create a task for the follow-up agent to analyze a contact

    Args:
        agent: The follow-up scheduler agent
        contact_data: Dictionary with contact and conversation information

    Returns:
        Task configured for follow-up analysis
    """
    name = contact_data.get('name', 'Contact')
    conversation = contact_data.get('conversation_summary', '')
    topics = contact_data.get('topics_discussed', [])
    action_items = contact_data.get('follow_ups', [])

    description = f"""
    Analyze this networking conversation and create a follow-up strategy:

    Contact: {name}
    Company: {contact_data.get('company', 'N/A')}
    Role: {contact_data.get('role', 'N/A')}

    Conversation Summary:
    {conversation}

    Topics Discussed:
    {', '.join(topics) if topics else 'N/A'}

    Mentioned Action Items:
    {', '.join(action_items) if action_items else 'None mentioned'}

    Your task:
    1. **Urgency Analysis**
       - Determine follow-up urgency (immediate, 1-day, 3-days, 1-week, 2-weeks)
       - Consider: explicit commitments, time-sensitive opportunities, interest level

    2. **Priority Score** (0-100)
       - Evaluate potential value of this connection
       - Consider: seniority, mutual interests, business opportunity, network value

    3. **Follow-up Recommendations**
       - Suggest optimal timing for first follow-up
       - Suggest follow-up medium (email, LinkedIn, WhatsApp, phone)
       - List 2-3 specific conversation hooks to reference

    4. **Message Generation**
       - Draft 2 personalized follow-up message templates:
         a) Short version (for LinkedIn/text)
         b) Detailed version (for email)
       - Reference specific topics from conversation
       - Include clear call-to-action

    5. **Action Item Tracking**
       - Extract concrete action items with deadlines
       - Categorize by owner (you vs them)

    6. **Relationship Building Strategy**
       - Suggest 3 ways to add value to this contact
       - Identify potential collaboration opportunities
       - Recommend content/resources to share
    """

    expected_output = """
    A structured JSON response with:
    {
        "urgency": "immediate|1-day|3-days|1-week|2-weeks",
        "priority_score": 85,
        "priority_reason": "High-level decision maker, expressed interest in collaboration",
        "optimal_timing": {
            "first_followup": "2026-03-06T10:00:00Z",
            "medium": "email",
            "reason": "Professional context requires formal communication"
        },
        "conversation_hooks": [
            "AI safety discussion",
            "Mentioned upcoming conference",
            "Shared interest in interpretability"
        ],
        "messages": {
            "short": "Hi [Name], great connecting at [Event]! Would love to continue our chat about [Topic]. Free for a quick call next week?",
            "detailed": "Full email template with introduction, body, and call-to-action"
        },
        "action_items": [
            {
                "item": "Send GitHub repo",
                "owner": "you",
                "deadline": "2026-03-07",
                "status": "pending"
            }
        ],
        "value_adds": [
            "Introduce to [Mutual Contact] working on similar problems",
            "Share recent research paper on [Topic]",
            "Invite to internal tech talk"
        ],
        "collaboration_opportunities": [
            "Potential partnership on [Project]",
            "Speaking opportunity at [Event]"
        ],
        "next_touchpoints": [
            {"date": "2026-03-06", "action": "Send initial follow-up"},
            {"date": "2026-03-13", "action": "Check in on [Action Item]"},
            {"date": "2026-04-01", "action": "Monthly check-in"}
        ]
    }
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )


def create_followup_strategy(contact_data: Dict) -> Dict:
    """
    Main function to create follow-up strategy for a contact

    Args:
        contact_data: Dictionary with contact and conversation information

    Returns:
        Follow-up strategy with timing, messages, and action items

    Example:
        >>> contact = {"name": "Sarah Chen", "conversation_summary": "Discussed AI safety..."}
        >>> strategy = create_followup_strategy(contact)
        >>> print(strategy['messages']['short'])
    """
    try:
        # Create agent
        followup_agent = create_followup_scheduler()

        # Create task
        followup_task = create_followup_task(followup_agent, contact_data)

        # For demo, generate intelligent mock data based on conversation
        strategy = generate_intelligent_followup(contact_data)

        return strategy

    except Exception as e:
        print(f"[ERROR] Follow-up strategy generation failed: {e}")
        # Return basic strategy if generation fails
        return create_basic_followup(contact_data)


def generate_intelligent_followup(contact_data: Dict) -> Dict:
    """
    Generate intelligent follow-up strategy based on conversation context

    This analyzes the conversation to determine:
    - Urgency (based on action items and context)
    - Priority (based on role, company, engagement level)
    - Optimal timing and medium
    - Personalized messages

    Args:
        contact_data: Contact and conversation information

    Returns:
        Comprehensive follow-up strategy
    """
    name = contact_data.get('name', 'Contact')
    first_name = name.split()[0] if name else 'there'
    company = contact_data.get('company', 'their company')
    role = contact_data.get('role', 'professional')
    topics = contact_data.get('topics_discussed', [])
    action_items = contact_data.get('follow_ups', [])
    conversation = contact_data.get('conversation_summary', '')
    event = contact_data.get('met_at', 'our recent conversation')

    # Determine urgency based on action items and keywords
    urgency = determine_urgency(conversation, action_items)

    # Calculate priority score based on multiple factors
    priority_score = calculate_priority_score(contact_data)

    # Generate optimal timing
    timing = calculate_optimal_timing(urgency)

    # Generate personalized messages
    messages = generate_personalized_messages(
        first_name, name, event, topics, action_items, company, role
    )

    # Extract and structure action items
    structured_actions = structure_action_items(action_items)

    # Generate value-add suggestions
    value_adds = generate_value_adds(topics, role, company)

    strategy = {
        'urgency': urgency,
        'priority_score': priority_score,
        'priority_reason': f'Engaged discussion on {len(topics)} topics, {len(action_items)} action items mentioned',
        'optimal_timing': timing,
        'conversation_hooks': topics[:3] if topics else ['your interesting conversation'],
        'messages': messages,
        'action_items': structured_actions,
        'value_adds': value_adds,
        'collaboration_opportunities': generate_collaboration_ideas(topics, role),
        'next_touchpoints': generate_touchpoint_schedule(timing['first_followup']),
        'generated_at': datetime.utcnow().isoformat()
    }

    return strategy


def determine_urgency(conversation: str, action_items: List[str]) -> str:
    """Determine urgency based on conversation content"""
    conversation_lower = conversation.lower()

    if any(word in conversation_lower for word in ['urgent', 'asap', 'immediately', 'today']):
        return 'immediate'
    elif action_items and len(action_items) > 0:
        return '1-day'
    elif any(word in conversation_lower for word in ['soon', 'next week', 'follow up']):
        return '3-days'
    elif any(word in conversation_lower for word in ['interested', 'potential', 'opportunity']):
        return '1-week'
    else:
        return '2-weeks'


def calculate_priority_score(contact_data: Dict) -> int:
    """Calculate priority score (0-100) based on contact factors"""
    score = 50  # Base score

    # Role-based scoring
    role = contact_data.get('role', '').lower()
    if any(title in role for title in ['ceo', 'founder', 'director', 'vp', 'head']):
        score += 20
    elif any(title in role for title in ['lead', 'senior', 'principal']):
        score += 10

    # Engagement scoring
    topics = contact_data.get('topics_discussed', [])
    score += min(len(topics) * 5, 20)  # Up to +20 for topics

    action_items = contact_data.get('follow_ups', [])
    score += min(len(action_items) * 10, 20)  # Up to +20 for action items

    # Company scoring (if known prestigious company)
    company = contact_data.get('company', '').lower()
    if any(name in company for name in ['google', 'microsoft', 'amazon', 'meta', 'apple']):
        score += 10

    return min(score, 100)  # Cap at 100


def calculate_optimal_timing(urgency: str) -> Dict:
    """Calculate optimal follow-up timing based on urgency"""
    now = datetime.utcnow()

    urgency_map = {
        'immediate': timedelta(hours=2),
        '1-day': timedelta(days=1),
        '3-days': timedelta(days=3),
        '1-week': timedelta(weeks=1),
        '2-weeks': timedelta(weeks=2)
    }

    delta = urgency_map.get(urgency, timedelta(days=3))
    followup_time = now + delta

    # Adjust to business hours (10 AM)
    followup_time = followup_time.replace(hour=10, minute=0, second=0)

    return {
        'first_followup': followup_time.isoformat() + 'Z',
        'medium': 'email' if urgency in ['1-week', '2-weeks'] else 'linkedin',
        'reason': 'Professional context' if urgency in ['1-week', '2-weeks'] else 'Maintain momentum'
    }


def generate_personalized_messages(first_name: str, full_name: str, event: str,
                                   topics: List[str], action_items: List[str],
                                   company: str, role: str) -> Dict:
    """Generate personalized follow-up messages"""
    topic_mention = topics[0] if topics else 'our conversation'

    short_message = (
        f"Hi {first_name}, great connecting at {event}! "
        f"Really enjoyed discussing {topic_mention}. "
        f"Would love to stay connected and continue the conversation!"
    )

    # Build detailed message parts to avoid f-string backslash issues
    insights_line = f"Your insights on {topics[1]} were particularly interesting." if len(topics) > 1 else "I found your perspective really valuable."
    action_line = f"As mentioned, I'll {action_items[0].lower()}. " if action_items else ""

    detailed_message = f"""Subject: Great connecting at {event}!

Hi {first_name},

It was a pleasure meeting you at {event}! I really enjoyed our conversation about {topic_mention}.

{insights_line}

{action_line}I'd love to stay connected and explore potential collaboration opportunities.

Are you available for a quick 15-minute call next week? I'd be happy to work around your schedule.

Looking forward to staying in touch!

Best regards,
[Your Name]
"""

    return {
        'short': short_message,
        'detailed': detailed_message
    }


def structure_action_items(action_items: List[str]) -> List[Dict]:
    """Structure action items with deadlines and ownership"""
    structured = []

    for item in action_items:
        structured.append({
            'item': item,
            'owner': 'you',  # Could be enhanced with NLP to detect owner
            'deadline': (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'pending'
        })

    return structured


def generate_value_adds(topics: List[str], role: str, company: str) -> List[str]:
    """Generate value-add suggestions based on topics and role"""
    value_adds = [
        f"Share relevant article or research on {topics[0]}" if topics else "Share industry insights",
        f"Introduce to connection at {company}" if company else "Introduce to relevant contact",
        "Invite to upcoming industry event or webinar"
    ]

    return value_adds


def generate_collaboration_ideas(topics: List[str], role: str) -> List[str]:
    """Generate potential collaboration opportunities"""
    collaborations = []

    if topics:
        collaborations.append(f"Potential collaboration on {topics[0]} project")

    if any(word in role.lower() for word in ['engineer', 'developer', 'technical']):
        collaborations.append("Technical collaboration or code review")

    if any(word in role.lower() for word in ['manager', 'director', 'lead']):
        collaborations.append("Strategic partnership discussion")

    return collaborations if collaborations else ["Exploratory discussion on mutual interests"]


def generate_touchpoint_schedule(first_followup: str) -> List[Dict]:
    """Generate schedule of future touchpoints"""
    first = datetime.fromisoformat(first_followup.replace('Z', '+00:00'))

    touchpoints = [
        {
            'date': first.strftime('%Y-%m-%d'),
            'action': 'Send initial follow-up'
        },
        {
            'date': (first + timedelta(weeks=1)).strftime('%Y-%m-%d'),
            'action': 'Check in on action items'
        },
        {
            'date': (first + timedelta(weeks=4)).strftime('%Y-%m-%d'),
            'action': 'Monthly check-in with value add'
        }
    ]

    return touchpoints


def create_basic_followup(contact_data: Dict) -> Dict:
    """Create basic follow-up strategy as fallback"""
    name = contact_data.get('name', 'Contact')

    return {
        'urgency': '3-days',
        'priority_score': 70,
        'priority_reason': 'Standard networking follow-up',
        'optimal_timing': {
            'first_followup': (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z',
            'medium': 'email',
            'reason': 'Professional standard'
        },
        'messages': {
            'short': f"Hi {name.split()[0]}, great meeting you! Let's stay connected.",
            'detailed': f"Subject: Great connecting!\n\nHi {name.split()[0]},\n\nIt was great meeting you. "
                       f"Let's stay in touch!\n\nBest,\n[Your Name]"
        }
    }


# Example usage
if __name__ == "__main__":
    # Test the agent with sample contact data
    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment", "Interpretability"],
        "follow_ups": ["Send GitHub repo", "Connect on LinkedIn"],
        "conversation_summary": "Discussed AI safety work at Google focusing on LLM alignment.",
        "met_at": "DevFest Kolkata 2026"
    }

    print("\n" + "="*70)
    print("TESTING FOLLOW-UP SCHEDULER AGENT")
    print("="*70)

    strategy = create_followup_strategy(sample_contact)

    print("\nFollow-up Strategy:")
    print(json.dumps(strategy, indent=2))

    print("\n" + "="*70)
    print("[OK] Follow-up agent test complete!")
    print("="*70)
